"""
返回数据统一封装类
"""
import json
from django.http import HttpResponse

class WrapResponseDataMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        response = self.packing_response(response)
        return response

    def packing_response(self, response):
        """
        打包返回小消息体
        """
        if not hasattr(response, 'data'):
            return response
        data = response.data
        if isinstance(data, str):
            res = {
                "msg": data,
                "code": 500
            }
        else:
            res = {
                "msg": "ok",
                "data": data,
                "code": 200
            }
        response.data = res
        response.content = json.dumps(res).encode("utf-8")
        return response

    def process_exception(self, request, exception):
        """
        全局的异常处理
        """
        if isinstance(exception, RuntimeError):
            msg = exception.args[0]
            response = HttpResponse()
            response.data = msg
            return response
        return None
