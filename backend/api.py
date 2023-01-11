from typing import Dict, Any, Optional

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
    def get(self, request: HttpRequest):
        if settings.DEBUG:
            test_query()


class Signup(Handler):

    def post(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        create_user(name=data['userName'], email=data['email'],
                    passwd=hash_passwd(data['password']))


class Login(Handler):

    def post(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        name_or_email = data.get('name', '') or data['email']
        assert name_or_email, 'Bad login params.'
        user_uri = check_passwd(
            name_or_email, hash_passwd(data['password']))
        return {
            'token': auth_sign({
                'user': user_uri,
            })
        }


class UserInfo(AuthedHandler):

    def get(self, request: HttpRequest) -> Dict[str, Any]:
        user_info = get_user_info(self.user_uir)
        user_info.update(userName=user_info.pop('name'))
        return user_info

    def post(self, data: Dict[str, Any]):
        data.update(name=data.pop('userName', ''))
        modify_user_info(self.user_uir, **data)


class Weibo(AuthedHandler, PaginationMixin):

    def get(self, request: HttpRequest) -> Dict[str, Any]:
        return self.pagination(request, get_weibo(self.user_uir))

    def map(self, elem: str) -> Dict[str, Any]:
        weibo_uri = elem
        (user_uri, uname, uavatar, text, time) = get_weibo_info(weibo_uri)
        return {
            'uid': user_uri[user_uri.rfind('#') + 1: -1],
            'userName': uname,
            'avatar': uavatar,
            'message': text,
            'createTime': time.strftime('%Y-%m-%d %H:%M:%S')
        }


class WeiboSend(AuthedHandler):

    def post(self, data: Dict[str, Any]):
        post_weibo(self.user_uir, message=data['message'])


class Friend(AuthedHandler, PaginationMixin):

    def get(self, request: HttpRequest) -> Dict[str, Any]:
        if request.GET['type'] == 'followers':
            result = followers(self.user_uir)
        elif request.GET['type'] == 'concerns':
            result = concerns(self.user_uir)
        else:
            raise NotImplementedError
        return self.pagination(request, result, adapt_uinfo)


class FriendFollow(AuthedHandler):

    def post(self, data: Dict[str, Any]):
        follow(self.user_uir, data['uid'])


class FriendUnfollow(AuthedHandler):
    def post(self, data: Dict[str, Any]):
        unfollow(self.user_uir, data['uid'])


class FriendFind(AuthedHandler, PaginationMixin):

    def get(self, request: HttpRequest) -> Dict[str, Any]:
        return self.pagination(request,
                               find_user(name=request.GET['userName']),
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
