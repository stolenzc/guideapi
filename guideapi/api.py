import inspect
import os
from collections import defaultdict
# TODO @stolenzc after Python3.9 can replace List to list, Tuple to tuple, Dict to dict
from typing import Any, Dict, List, Tuple, Union

from jinja2 import Environment, FileSystemLoader
from parse import parse
from webob import Request, Response

from .exception import MethodNotAllowed, NotFound
from .response_type import ResponseType


class API(object):

    def __init__(self, templates_dir="templates"):
        """
        routes is a dict to store the route, which have two ways to store different handler
        1. if the handler is a function, the value is a dict, the key is the request method,
        and the value is the handler
        2. if the handler is a class, the value is a object, which can find the class handler
        """
        self.routes: defaultdict[str, Any] = defaultdict(dict)
        self.templates_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))

    def route(self, path: str, methods: Union[str, List[str]] = 'get'):
        """
        decorator for add route
        """

        def wrapper(handler):
            self.add_route(path, handler, methods)
            # inspect.getmembers(handler, lambda a: inspect.isfunction(a))
            # get class member
            return handler

        return wrapper

    def add_route(self, path: str, handler: object, methods: Union[str, List[str]] = 'get'):
        """
        add route to router dict
        Args:
            path: request path
            handler: function
            methods: request method
        Returns:
            None
        Raises:
            AssertionError: if path in router dict
        """
        if inspect.isclass(handler):
            self.routes[path] = handler
        else:
            if isinstance(methods, str):
                methods = [methods.lower()]
            if isinstance(methods, list):
                methods = [method.lower() for method in methods]
            for method in methods:
                self.routes[path][method] = handler

    def find_handler(self, request_path: str, request_method: str):
        """
        find hander from router dict by request path
        Args:
            request_path: request path
        Returns:
            handler: function
            named: real path
        """
        for path in self.routes:
            # regular expression to find path
            parse_result = parse(path, request_path)
            if parse_result is not None:
                handler = self.routes[path]
                if inspect.isclass(handler):
                    handler = getattr(handler(), request_method.lower(), None)
                else:
                    handler = handler.get(request_method.lower())
                if not handler:
                    raise MethodNotAllowed()
                # return handler and original path
                return handler, parse_result.named  # type: ignore
        raise NotFound()

    def wsgi_app(self, environ, start_response):
        """
        input request, and return the response
        Args:
            environ: wsgi environ
            start_response: request info
        Returns:
            response: response
        """
        request = Request(environ)
        response = self.handle_request(request)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def handle_request(self, request: Request) -> Response:
        """
        deal with the handler
        """

        response = Response()
        request_method = request.method.lower()
        try:
            handler, kwargs = self.find_handler(request.path, request_method)
        except MethodNotAllowed:
            self.not_found(response)
            return response
        except NotFound:
            self.method_not_allowed(response)
            return response

        handler_response = handler(request, response, **kwargs)
        if handler_response and isinstance(handler_response, str):
            response.text = handler_response
        return response

    def set_response_status(self, response: Response, status_type: Tuple[int, str]):
        """
        set response http code and message
        """
        response.status_code, response.text = status_type

    def not_found(self, response):
        """
        default not found response
        """
        self.set_response_status(response, ResponseType.STATUS_404)

    def method_not_allowed(self, response):
        """
        default method not allowed response
        """
        self.set_response_status(response, ResponseType.STATUS_405)

    def template(self, template_name, context=None):
        """
        deal with template
        """
        if context is None:
            context = {}
        return self.templates_env.get_template(template_name).render(**context)
