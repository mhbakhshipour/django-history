from threading import local
from django.utils.deprecation import MiddlewareMixin

_thread_locals = local()


def current_request():
    return getattr(_thread_locals, 'request', None)


class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _thread_locals.request = request

    def process_response(self, request, response):
        # Clean up the request after the response is processed
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

    def process_exception(self, request, exception):
        # Clean up the request if an exception occurs
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
