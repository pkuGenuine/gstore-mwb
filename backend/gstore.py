from typing import Dict, List, Any
from datetime import datetime

from backend.gstore_helpers import select, ask, update
from utils.general import glock, get_uuid
from utils.namespace import MiniWeiboNamespace, RDFNamespace, literal_n3


def create_user(name: str, passwd: str, email: str, location: str = '', gender: str = ''):
    name = literal_n3(name)
    passwd = literal_n3(passwd)
    email = literal_n3(email)
    location = literal_n3(location)
    gender = literal_n3(gender)
    literal_zero = literal_n3(0)
    ask_dup_sparql = f"""
    ask {{
        {{
            ?x :name {name}
        }} union {{ 
            ?x :name {email}
        }} union {{ 
            ?x :email {name}
        }} union {{
            ?x :email {email}
        }}
    }}
    """
    assert not ask(ask_dup_sparql), 'Name or email already used'
    create_user_sparql = f"""
    insert data {{
        {MiniWeiboNamespace.UserURI(get_uuid())} rdf:type :User ;
            :name {name} ;
            :passwd {passwd} ;
            :email {email} ;
            :location {location} ;
            :gender {gender} ;
            :follower-num {literal_zero} ;
            :friend-num {literal_zero} ;
            :statues-num {literal_zero} ;
            :favourite-num {literal_zero} ;
            :created-at {literal_n3(datetime.now())} .
    }}
    """
    update(create_user_sparql)


def check_passwd(name_or_email: str, passwd: str) -> str:
    name_or_email = literal_n3(name_or_email)
    passwd = literal_n3(passwd)
    find_user_sparql = f"""
    where {{
        ?x :name {name_or_email} ;
            :passwd {passwd} .
    }} union select ?x
    where {{
        ?x :email {name_or_email} ;
            :passwd {passwd} .
    }}
    """
    result = select('x', find_user_sparql)
    print(result)
    assert len(result) == 1, 'Unexpected err, multiple match.'
    return result[0]


def get_user_info(user_uri: str) -> Dict[str, Any]:
    cond = f"""
    where {{
        {user_uri} ?x ?y .
        filter(?x != {MiniWeiboNamespace.follow})
        filter(?x != {MiniWeiboNamespace.passwd})
        filter(?x != {RDFNamespace._type})
    }}
    """
    result = select(['x', 'y'], cond)
    result = {k[k.rfind('#') + 1: -1]: v for (k, v) in result}
    result.update(
        uid=user_uri[user_uri.rfind('#') + 1: -1],
    )
    return result


def modify_user_info(user_uri: str, **kwargs):
    # TODO: with lock & handle failure
    # old_info = get_user_info(user_uri)
    template = f"""
    delete {{
        {user_uri} $property$ ?x .
    }} insert {{
        {user_uri} $property$ $new$ .
    }} where {{
        {user_uri} $property$ ?x .
    }}
    """
    delete_temp = f"""
    delete {{
        {user_uri} $property$ ?x .
    }} where {{
        {user_uri} $property$ ?x .
    }}
    """
    insert_temp = f"""
    insert data {{
        {user_uri} $property$ $new$ .
    }}
    """

    for k in ['name', 'email', 'location', 'gender']:
        v = kwargs.get(k, '')
        if v:
            # TODO: There are bugs in gstore, can not use update syntax...
            # update(template.replace('$property$',
            #        f':{k}').replace('$new$', literal_n3(v)))
            update(delete_temp.replace('$property$', f':{k}'))
            update(insert_temp.replace('$property$',
                   f':{k}').replace('$new$', literal_n3(v)))


def followers(user_uri: str) -> List[str]:
    sparql = f"""
    where {{
        ?x :follow {user_uri} .
    }}
    """
    return select('x', sparql)


def concerns(user_uri: str) -> List[str]:
    sparql = f"""
    where {{
        {user_uri} :follow ?x .
    }}
    """
    return select('x', sparql)


def follow(s_uri: str, t_uid: str):
    sparql = f"""
        insert data {{
            {s_uri} :follow {MiniWeiboNamespace.UserURI(t_uid)} .
    }}
    """
    update(sparql)


def unfollow(s_uri: str, t_uri: str):
    sparql = f"""
        delete data {{
            {s_uri} :follow {t_uri} .
    }}
    """
    update(sparql)


def find_user(name: str) -> List[str]:
    cond = f"""
        where {{
            ?x :name ?y .
            filter regex(?y, {literal_n3(name)})
        }}
    """
    return select('x', cond)


def get_weibo(user_uri: str) -> List[str]:
    sparql = f"""
    where {{
        {user_uri} :follow ?y .
        ?y :post ?x .
        ?x :created-at ?t .
    }}
    """
    return [t[0] for t in sorted(select(['x', 't'], sparql),
                                 key=lambda x: x[1], reverse=True)]


def my_weibo(user_uri: str) -> List[str]:
    sparql = f"""
    where {{
        {user_uri} :post ?x .
    }}
    """
    return select('x', sparql)


def get_weibo_info(weibo_uri: str) -> List[Any]:
    cond = f"""
    where {{
        ?user :post {weibo_uri} ;
            :name ?uname .
        {weibo_uri} :text ?content ;
            :created-at ?t .
    }}
    """
    result = select(['user', 'uname', 'content', 't'], cond)
    assert len(result) == 1
    return result[0]


def post_weibo(user_uri: str, message: str, topic: str = ''):
    # TODO: support topic
    # handle escape
    wid = get_uuid()
    weibo_uri = MiniWeiboNamespace.WeiboURI(wid)
    sparql = f"""
    insert data {{
        {weibo_uri} rdf:type :Weibo ;
            :text {literal_n3(message)} ;
            :datetime {literal_n3(datetime.now())} .
        {user_uri} :post {weibo_uri}.
    }}
    """
    update(sparql)


def test_query():
    cond = f"""
    where {{
    }}
    """
    select('x', cond)
