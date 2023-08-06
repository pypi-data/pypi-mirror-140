from typing import Callable, Optional

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin


class HawkResponseMiddleware(MiddlewareMixin):
    def __init__(self, get_response: Optional[Callable] = None) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:

        if not self.get_response:
            raise Exception("get_response is not defined")

        response = self.get_response(request)

        response["Server-Authorization"] = request.auth.respond(  # type: ignore
            content=response.content,
            content_type=response["Content-Type"],
        )

        return response
