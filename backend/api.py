from typing import Dict, List, Any, Optional

from django.http import HttpRequest
from django.conf import settings

from utils.general import auth_sign, hash_passwd
from utils.response import Handler, AuthedHandler, PaginationMixin
from backend.gstore import (
    create_user, check_passwd,
    get_user_info, modify_user_info,
    follow, unfollow,
    followers, concerns, find_user,
    get_weibo, get_weibo_info, post_weibo,
    test_query
)


class Test(Handler):
    def handle_get(self, request: HttpRequest):
        if settings.DEBUG:
            test_query()


class Signup(Handler):

    def handle_post(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        create_user(name=request.POST['userName'], email=request.POST['email'],
                    passwd=hash_passwd(request.POST['password']))


class Login(Handler):

    def handle_post(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        name_or_email = request.POST.get('name', '') or request.POST['email']
        assert name_or_email, 'Bad login params.'
        user_uri = check_passwd(
            name_or_email, hash_passwd(request.POST['passwd']))
        return {
            'token': auth_sign({
                'user': user_uri,
            })
        }


class UserInfo(AuthedHandler):

    def handle_get(self, request: HttpRequest) -> Dict[str, Any]:
        user_info = get_user_info(self.user_uir)
        user_info.update(userName=user_info.pop('name'))
        return user_info

    def handle_post(self, request: HttpRequest):
        new_info = {k: v for (k, v) in request.POST.items()}
        new_info.update(name=new_info.pop('userName', ''))
        modify_user_info(self.user_uir, **new_info)


class Weibo(AuthedHandler, PaginationMixin):

    def handle_get(self, request: HttpRequest) -> Dict[str, Any]:
        return self.pagination(request, get_weibo(self.user_uir))

    def map(self, weibo_uri: List[Any]) -> Dict[str, Any]:
        (user_uri, uname, text, time) = get_weibo_info(weibo_uri)
        return {
            'uid': user_uri[user_uri.rfind('#') + 1: -1],
            'userName': uname,
            'message': text,
            'createTime': time.strftime('%Y-%m-%d %H:%M:%S')
        }


class WeiboSend(AuthedHandler):

    def handle_post(self, request: HttpRequest):
        post_weibo(self.user_uir, message=request.POST['message'])


class Friend(AuthedHandler, PaginationMixin):

    def handle_get(self, request: HttpRequest) -> Dict[str, Any]:
        if request.GET['type'] == 'followers':
            result = followers(self.user_uir)
        elif request.GET['type'] == 'concerns':
            result = concerns(self.user_uir)
        else:
            raise NotImplementedError
        return self.pagination(request, result, adapt_uinfo)


class FriendFollow(AuthedHandler):

    def handle_post(self, request: HttpRequest):
        follow(self.user_uir, request.POST['uid'])


class FriendFind(AuthedHandler, PaginationMixin):

    def handle_get(self, request: HttpRequest) -> Dict[str, Any]:
        return self.pagination(request, find_user(name=request.GET['userName']),
                               adapt_uinfo)


def adapt_uinfo(user_uri: str) -> Dict[str, Any]:
    userinfo = get_user_info(user_uri)
    return dict(
        uid=user_uri[user_uri.rfind('#') + 1: -1],
        userName=userinfo.pop('name'),
        # TODO:
        # 1. friends = concerns?
        # 2. Keep count or calculate on the fly
        followersnum=len(followers(user_uri)),
        concernsnum=len(concerns(user_uri)),
        # followersnum=userinfo.pop('follower-num'),
        # concernsnum=userinfo.pop('friend-num'), 
        weibonum=len(get_weibo(user_uri))
    )