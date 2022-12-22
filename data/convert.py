from typing import Iterable, List, Tuple, Any
from datetime import datetime
import sys
import os

import sqlparse
from rdflib import Literal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.namespace import MiniWeiboNamespace


def n3literal(data: Any) -> str:
    return Literal(data).n3()


def row2rdf(table: str, tokens: Iterable) -> List[Tuple[Any, Any, Any]]:
    d = {
        'user': user2rdf,
        'weibo': weibo2rdf,
        'userrelation': follow2rdf,
        'weiborelation': repost2rdf
    }
    return d[table](filter(lambda x: x not in ['VALUES', '', ' ', ',', '(', ')'], map(lambda x: x.value, tokens)))


def next_single(tokens: Iterable[str], literal=True) -> str:
    ret = next(tokens).strip('\'')
    if literal:
        return Literal(ret).n3()
    return ret


def next_integer(tokens: Iterable[str]) -> str:
    return n3literal(int(next(tokens)))


def next_datetime(tokens: Iterable[str]) -> str:
    return n3literal(datetime.strptime(next(tokens).strip('\''), '%Y-%m-%d %H:%M:%S'))


def user2rdf(tokens: Iterable) -> List[Tuple[Any, Any, Any]]:
    ret = []
    uid = next_single(tokens, literal=False)
    user = MiniWeiboNamespace.UserURI(uid)
    ret.extend(user.info_tuples)
    ret.append((user, MiniWeiboNamespace.name, next_single(tokens)))
    _screen_name = next_single(tokens)
    ret.append((user, MiniWeiboNamespace.province, next_integer(tokens)))
    ret.append((user, MiniWeiboNamespace.city, next_integer(tokens)))
    ret.append((user, MiniWeiboNamespace.location, next_single(tokens)))
    ret.append((user, MiniWeiboNamespace.url, next_single(tokens)))
    ret.append((user, MiniWeiboNamespace.gender, next_single(tokens)))
    ret.append((user, MiniWeiboNamespace.follower_num, next_integer(tokens)))
    ret.append((user, MiniWeiboNamespace.friend_num, next_integer(tokens)))
    ret.append((user, MiniWeiboNamespace.statues_num, next_integer(tokens)))
    ret.append((user, MiniWeiboNamespace.favourite_num, next_integer(tokens)))
    ret.append((user, MiniWeiboNamespace.created_at, next_datetime(tokens)))
    return ret


def follow2rdf(tokens: Iterable) -> List[Tuple[Any, Any, Any]]:
    suid = next_single(tokens, literal=False)
    tuid = next_single(tokens, literal=False)
    return [(MiniWeiboNamespace.UserURI(suid),
            MiniWeiboNamespace.follow, MiniWeiboNamespace.UserURI(tuid))]


def weibo2rdf(tokens: Iterable) -> List[Tuple[Any, Any, Any]]:
    ret = []
    weibo_id = next_single(tokens, literal=False)
    weibo = MiniWeiboNamespace.WeiboURI(weibo_id)
    ret.extend(weibo.info_tuples)
    ret.append((weibo, MiniWeiboNamespace.created_at, next_datetime(tokens)))
    ret.append((weibo, MiniWeiboNamespace.text, next_single(tokens)))
    ret.append((weibo, MiniWeiboNamespace.source, next_single(tokens)))
    ret.append((weibo, MiniWeiboNamespace.repost_num, next_integer(tokens)))
    ret.append((weibo, MiniWeiboNamespace.comment_num, next_integer(tokens)))
    ret.append((weibo, MiniWeiboNamespace.attitude_num, next_integer(tokens)))
    uid = next_single(tokens, literal=False)
    user = MiniWeiboNamespace.UserURI(uid)
    ret.append((user, MiniWeiboNamespace.post, weibo))
    ret.append((weibo, MiniWeiboNamespace.topic, next_single(tokens)))
    return ret


def repost2rdf(tokens: Iterable) -> List[Tuple[Any, Any, Any]]:
    smid = next_single(tokens, literal=False)
    tmid = next_single(tokens, literal=False)
    return [(MiniWeiboNamespace.WeiboURI(smid),
            MiniWeiboNamespace.repost, MiniWeiboNamespace.WeiboURI(tmid))]


if __name__ == '__main__':
    with open('weibodatabase.sql') as f:
        with open('weibo.nt', 'w') as fw:
            for (s, p, o) in MiniWeiboNamespace.info_tuples:
                fw.write(f'{s} {p} {o} .\n')
            for line in filter(lambda l: l.startswith('INSERT'), f):
                tokens = sqlparse.parse(line)[0]
                table = tokens[4].get_name()
                for (s, p, o) in row2rdf(table, tokens[-2].flatten()):
                    fw.write(f'{s} {p} {o} .\n')
