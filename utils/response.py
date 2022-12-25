from typing import Dict, Any, Callable, Optional, List

from django import views
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings

from utils.general import auth_verify


Response = HttpResponse | JsonResponse
Http401Response = HttpResponse('Unauthorized', status=401)
Http400Response = HttpResponse('Bad Request', status=400)


class Handler(views.View):

    def auth(self, request: HttpRequest) -> bool:
        return True

    def get(self, request: HttpRequest) -> Response:
        return self.handle(request, self.handle_get)

    def post(self, request: HttpRequest) -> Response:
        return self.handle(request, self.handle_post)

    def handle(self, request: HttpRequest, handler: Callable[[HttpRequest], None | Dict[str, Any]]) -> Response:
        if not self.auth(request):
            return Http401Response
        try:
            response = handler(request)
            if response is None:
                return HttpResponse("OK")
            return JsonResponse(response)
        except:
            if settings.DEBUG:
                raise
        return Http400Response

    def handle_get(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def handle_post(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class AuthedHandler(Handler):

    user_uir: str

    def auth(self, request: HttpRequest) -> bool:
        self.user_uir = auth_verify(request.headers['Authorization'])
        return True


class PaginationMixin():

    def pagination(self, request: HttpRequest, l: List[Any],
                   f: Optional[Callable[[Any], Any]] = None) -> Dict[str, Any]:
        size = int(request.GET['size'])
        page = int(request.GET['page'])
        f = f or self.map
        return {
            'current': page,
            'size': size,
            'total': len(l),
            'data': list(map(f, l[(page - 1) * size: page * size]))
        }

    def map(self, elem: Any) -> Any:
        raise NotImplementedError
