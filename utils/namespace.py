from typing import Optional, Tuple, List, Any
from functools import partial
from datetime import datetime

from rdflib import Literal, URIRef
from rdflib import RDF, RDFS


class MyURI:

    def __init__(self, v: str, prefix: str, prefix_label: str = '',
                 label: str = '', ty: Optional['MyURI'] = None,
                 formatter: str = 'n3'):
        assert formatter == 'n3', 'Currently only support n3 formatter.'
        self.formatter = lambda uri: URIRef(uri).n3()
        # TODO: add range & domain
        self.v = v
        self.label = label or v
        # Like http://...
        self.prefix = prefix
        # Like rdf
        self.prefix_label = prefix_label
        self.ty = ty

    def __str__(self) -> str:
        return self.formatter(self.prefix + self.v)

    @property
    def in_short(self) -> str:
        return f'{self.prefix_label}:{self.v}'

    @property
    def info_tuples(self) -> List[Tuple[str, str, str]]:
        ret = [
            # (str(self), RDFS.label.n3(), self.label)
        ]
        if self.ty is not None:
            ret.append(
                (str(self), RDF.type.n3(), str(self.ty))
            )
        return ret


class RDFNamespace:
    Class = MyURI('Class', str(RDFS))
    Class.ty = Class
    Property = MyURI('Property', str(RDF), Class)
    _type = MyURI('type', str(RDF), Property)


class MiniWeiboNamespace:
    PREFIX = 'http://fake-uri/miniweibo/volcab#'
    USER_PREFIX = 'http://fake-uri/miniweibo/user#'
    WEIBO_PREFIX = 'http://fake-uri/miniweibo/weibo#'

    User = MyURI('User', prefix=PREFIX, ty=RDFNamespace.Class)
    Weibo = MyURI('Weibo', prefix=PREFIX, ty=RDFNamespace.Class)

    __PROP = partial(MyURI, prefix=PREFIX, ty=RDFNamespace.Property)
    passwd = __PROP('passwd')
    name = __PROP('name')
    province = __PROP('province')
    city = __PROP('city')
    location = __PROP('location')
    url = __PROP('url')
    gender = __PROP('gender')
    follower_num = __PROP('follower-num')
    friend_num = __PROP('friend-num')
    statues_num = __PROP('statues-num')
    favourite_num = __PROP('favourite-num')
    created_at = __PROP('created-at')
    follow = __PROP('follow')
    text = __PROP('text')
    source = __PROP('source')
    repost_num = __PROP('repost-num')
    comment_num = __PROP('comment-num')
    attitude_num = __PROP('attitude-num')
    post = __PROP('post')
    topic = __PROP('topic')
    repost = __PROP('repost')

    UserURI = partial(MyURI, prefix=USER_PREFIX, ty=User)
    WeiboURI = partial(MyURI, prefix=WEIBO_PREFIX, ty=Weibo)


    info_tuples = []
    # TODO: Add all proper & label
    info_tuples.extend(User.info_tuples)
    info_tuples.extend(Weibo.info_tuples)
    info_tuples.extend(name.info_tuples)
    info_tuples.extend(passwd.info_tuples)

    def get_uid(user_uri: str) -> str:
        return user_uri[user_uri.rfind('#') + 1: -1]


def literal_n3(data: Any) -> str:
    if isinstance(data, datetime):
        data = data.replace(microsecond=0)
    return Literal(data).n3()