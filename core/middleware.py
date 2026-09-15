from threading import local

from django.conf import settings
from django.http import HttpResponse

_state = local()


def get_current_user():
    return getattr(_state, "user", None)


class CurrentUserMiddleware:
    """Stores the current user so model signals can create simple audit logs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _state.user = getattr(request, "user", None)
        try:
            return self.get_response(request)
        finally:
            _state.user = None


class MobileApiCorsMiddleware:
    """Allows the Expo web/mobile prototype to call the Django mobile API in dev."""

    MOBILE_API_PREFIX = "/api/mobile/"
    ALLOWED_METHODS = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    ALLOWED_HEADERS = "Authorization, Content-Type, Accept, X-Requested-With"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_mobile_api_request(request) and request.method == "OPTIONS":
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        if settings.DEBUG and self._is_mobile_api_request(request):
            origin = request.headers.get("Origin")
            response["Access-Control-Allow-Origin"] = origin or "*"
            response["Access-Control-Allow-Methods"] = self.ALLOWED_METHODS
            response["Access-Control-Allow-Headers"] = self.ALLOWED_HEADERS
            response["Access-Control-Max-Age"] = "86400"
            response["Vary"] = "Origin"

        return response

    def _is_mobile_api_request(self, request):
        return request.path.startswith(self.MOBILE_API_PREFIX)
