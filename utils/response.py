from typing import Dict, Any, Callable, Optional, List
import json
import logging

from django import views
from django.http import HttpRequest, HttpResponse, JsonResponse

from utils.general import auth_verify


Response = HttpResponse | JsonResponse
Http401Response = HttpResponse('Unauthorized', status=401)
Http400Response = HttpResponse('Bad Request', status=400)


class Handler(views.View):
    """
    A simply handler which assumes:
    1. Only support get and post
    2. All post data are json strings
    3. No authentication or, use header to auth
    """

    def _auth(self, request: HttpRequest) -> bool:
        return True

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        method = request.method
        try:
            if not self._auth(request):
                return Http401Response
            if not method or getattr(self, method.lower(), None) is None:
                return self.http_method_not_allowed(request)
            if method.lower() == 'get':
                response = self.get(request)
            elif method.lower() == 'post':
                response = self.post(json.loads(request.body))
            else:
                raise NotImplementedError
            if response is None:
                return HttpResponse('OK')
            return JsonResponse(response)
        except:
            logging.exception('')
        return Http400Response

    def get(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def post(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class AuthedHandler(Handler):

    user_uir: str

    def _auth(self, request: HttpRequest) -> bool:
        self.user_uir = auth_verify(request.headers['Authorization'])
        return self.user_uir != ''


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
