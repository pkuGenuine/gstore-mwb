from django.urls import path, include

from backend.api import *

auth_urls = [
    path("signup", Signup.as_view(), name='signup'),
    path("login", Login.as_view(), name='login')
]

user_urls = [
    path('', UserInfo.as_view(), name='user')
]

weibo_urls = [
    path('', Weibo.as_view(), name='weibo'),
    path('send', WeiboSend.as_view(), name='post weibo')
]

friend_urls = [
    path('follow', FriendFollow.as_view(), name='follow'),
    path('my-friends', Friend.as_view(), name='friends'),
    path('find-friends', FriendFind.as_view(), name='find friends')
]

api_urls = [
    path('test', Test.as_view(), name='test'),
    path('user', UserInfo.as_view(), name='user_alias'),
    path('weibo', Weibo.as_view(), name='weibo_alias'),
    path("auth/", include(auth_urls)),
    path('user/', include(user_urls)),
    path('weibo/', include(weibo_urls)),
    path('friend/', include(friend_urls))   
]

urlpatterns = [
    path('', include(api_urls)),
    path('api/', include(api_urls))
]
