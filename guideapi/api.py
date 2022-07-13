import inspect

from parse import parse
from webob import Request, Response


class API(object):

    def __init__(self):
        # url -> function
        self.routes = {}
        
    def route(self, path):
        """
        decorator for add route
        """
        def wrapper(handler):
            self.add_route(path, handler)
            return handler
        return wrapper

    def add_route(self, path, handler):
        """
        add route to router dict
        Args:
            path: request path
            handler: function
        Returns:
            None
        Raises:
            AssertionError: if path in router dict
        """
        # add_route, deal with same path
        assert path not in self.routes, "Such route already exists"
        self.routes[path] = handler

    def find_handler(self, request_path):
        """
        find hander from router dict by request path
        Args:
            request_path: request path
        Returns:
            handler: function
            named: real path
        """
        for path, handler in self.routes.items():
            # regular expression to find path
            parse_result = parse(path, request_path)
            if parse_result is not None:
                # 返回路由对应的方法和路由本身
                return handler, parse_result.named  # type: ignore
        return None, None

    def wsgi_app(self, environ, start_response):
        """
        request come in, handle request
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
        self.wsgi_app(environ, start_response)

    def handle_request(self, request):
        """请求调度"""

        response = Response()
        handler, kwargs = self.find_handler(request.path)

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    # find method in class handler
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None: # if method not found, not supported request method
                        raise AttributeError("Method now allowed", request.method)
                handler(request, response, **kwargs)
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
        response.text = "Not Found"
