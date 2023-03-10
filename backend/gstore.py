from typing import Dict, List, Any

from backend.gstore_helpers import select, select_x, ask, update, query, to_py
from utils.general import glock, get_uuid, now_time
from utils.namespace import MiniWeiboNamespace, RDFNamespace, literal_n3


def create_user(name: str, passwd: str, email: str, location: str = '', gender: str = '', avatar: str = ''):
    name = literal_n3(name)
    passwd = literal_n3(passwd)
    email = literal_n3(email)
    location = literal_n3(location)
    gender = literal_n3(gender)
    avatar = literal_n3(avatar)
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
            :avatar {avatar} ;
            :follower-num {literal_zero} ;
            :friend-num {literal_zero} ;
            :statues-num {literal_zero} ;
            :favourite-num {literal_zero} ;
            :created-at {literal_n3(now_time())} .
    }}
    """
    update(create_user_sparql)


def check_passwd(name_or_email: str, passwd: str) -> str:
    name_or_email = literal_n3(name_or_email)
    passwd = literal_n3(passwd)
    find_user_sparql = f"""
    where {{
        {{ ?x :name {name_or_email} ;
            :passwd {passwd} . }}
        union {{ ?x :email {name_or_email} ;
                    :passwd {passwd} . }}
    }}
    """
    result = select_x(find_user_sparql)
    assert len(result) == 1, 'Unexpected err, multiple match.'
    return result[0]


def get_user_info(user_uri: str) -> Dict[str, Any]:
    cond = f"""
    where {{
        {user_uri} ?x ?y .
        filter(?x != {MiniWeiboNamespace.follow})
        filter(?x != {MiniWeiboNamespace.passwd})
        filter(?x != {RDFNamespace.ty})
    }}
    """
    result = select(['x', 'y'], cond)
    result = {k[k.rfind('#') + 1: -1]: v for (k, v) in result}
    result.update(
        uid=user_uri[user_uri.rfind('#') + 1: -1],
    )
    return result


@glock
def modify_user_info(user_uri: str, **kwargs: Any):
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

    for k in ['name', 'email', 'location', 'gender', 'avatar']:
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
    return select_x(sparql)

def concerns_num(user_uri: str) -> int:
    sparql = f"""
    SELECT (count(?tag) as ?cnt) 
    WHERE {{ 
        {user_uri} :follow ?tag .
    }} 
    """
    return to_py(query(sparql)['results']['bindings'][0]['cnt']) #type: ignore

def follows_num(user_uri: str) -> int:
    sparql = f"""
    SELECT (count(?tag) as ?cnt) 
    WHERE {{ 
        ?tag :follow {user_uri} .
    }} 
    """
    return to_py(query(sparql)['results']['bindings'][0]['cnt']) #type: ignore


def weibo_num(user_uri: str) -> int:
    sparql = f"""
    SELECT (count(?tag) as ?cnt) 
    WHERE {{ 
        {user_uri} :post ?tag .
    }} 
    """
    return to_py(query(sparql)['results']['bindings'][0]['cnt']) #type: ignore



def concerns(user_uri: str) -> List[str]:
    sparql = f"""
    where {{
        {user_uri} :follow ?x .
    }}
    """
    return select_x(sparql)


def follow(s_uri: str, t_uid: str):
    sparql = f"""
        insert data {{
            {s_uri} :follow {MiniWeiboNamespace.UserURI(t_uid)} .
    }}
    """
    update(sparql)


def unfollow(s_uri: str, t_uid: str):
    sparql = f"""
        delete data {{
            {s_uri} :follow {MiniWeiboNamespace.UserURI(t_uid)} .
    }}
    """
    update(sparql)


def find_user(name: str) -> List[str]:
    cond = f"""
        where {{
            {{ ?x :name ?y .
                filter regex(?y, {literal_n3(name)}) . }} union 
            {{ ?x :name ?y .
                filter regex(str(?x), {literal_n3(name)}) }}
        }}
    """
    return select_x(cond)


def get_weibo(user_uri: str) -> List[str]:
    sparql = f"""
    where {{ 
        {{
            {user_uri} :post ?x .
        }} union {{
            {user_uri} :follow ?y .
            ?y :post ?x .
        }}
        ?x :created-at ?t .
    }}
    """

    return [t[0] for t in sorted(select(['x', 't'], sparql),
                                 key=lambda x: x[1], reverse=True)]


def get_weibo_info(weibo_uri: str) -> List[Any]:
    cond = f"""
    where {{
        ?user :post {weibo_uri} ;
            :name ?uname .
        {weibo_uri} :text ?cont ;
            :created-at ?t .
    }}
    """
    result = select(['user', 'uname', 'cont', 't'], cond)
    assert len(result) == 1
    return result[0]


def post_weibo(user_uri: str, message: str, topic: str = ''):
    # TODO: support topic
    wid = get_uuid()
    weibo_uri = MiniWeiboNamespace.WeiboURI(wid)
    sparql = f"""
    insert data {{
        {weibo_uri} rdf:type :Weibo ;
            :text {literal_n3(message)} ;
            :created-at {literal_n3(now_time())} .
        {user_uri} :post {weibo_uri}.
    }}
    """
    update(sparql)


def test_query():
    cond = f"""
    where {{
    }}
    """
    select_x(cond)
