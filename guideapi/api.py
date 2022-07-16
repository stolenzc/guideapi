import inspect
import os
from collections import defaultdict
# TODO @stolenzc after Python3.9 can replace List with list
from typing import List, Union

from jinja2 import Environment, FileSystemLoader
from parse import parse
from webob import Request, Response


class API(object):

    def __init__(self, templates_dir="templates"):
        # url -> function
        self.routes = defaultdict(dict)
        self.templates_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))

    def route(self, path: str, methods: Union[str, List[str]] = 'get'):
        """
        decorator for add route
        """

        def wrapper(handler):
            self.add_route(path, handler, methods)
            return handler

        return wrapper

    def add_route(self, path, handler, methods: Union[str, List[str]] = 'get'):
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
        if isinstance(methods, str):
            methods = [methods.lower()]
        if isinstance(methods, list):
            methods = [method.lower() for method in methods]
        for method in methods:
            assert path not in self.routes[method], "Such route already exists"
            self.routes[method][path] = handler

    def find_handler(self, request_path, request_method):
        """
        find hander from router dict by request path
        Args:
            request_path: request path
        Returns:
            handler: function
            named: real path
        """
        for path, handler in self.routes[request_method].items():
            # regular expression to find path
            parse_result = parse(path, request_path)
            if parse_result is not None:
                # 返回路由对应的方法和路由本身
                return handler, parse_result.named  # type: ignore
        return None, None

    def wsgi_app(self, environ, start_response):
        """
        input request, and return the response
        Args:
            environ: wsgi environ
            start_response: request info
        Returns:
            response: response
        """
        """通过 webob 将请求的环境信息转为request对象"""
        request = Request(environ)
        response = self.handle_request(request)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def handle_request(self, request):
        """
        deal with the handler
        """

        response = Response()
        request_method = request.method.lower()
        handler, kwargs = self.find_handler(request.path, request_method)

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    # find method in class handler
                    handler = getattr(handler(), request_method, None)
                    if handler is None:  # if method not found, not supported request method
                        raise AttributeError("Method now allowed", request.method)
                handler_response = handler(request, response, **kwargs)
                if handler_response and isinstance(handler_response, str):
                    response.text = handler_response
            else:
                # 返回默认错误
                self.defalut_response(response)
        except Exception as e:
            raise e
        return response

    def defalut_response(self, response):
        """
        default response, if no handler found, set the response for default response
        """
        response.status_code = 404
        response.text = "404 Not Found"

    def template(self, template_name, context=None):
        """
        deal with template
        """
        if context is None:
            context = {}
        return self.templates_env.get_template(template_name).render(**context)
