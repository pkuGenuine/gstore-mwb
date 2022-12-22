import os

from django.conf import settings


def get_env(env_var: str, default: str = '') -> str:
    if not settings.DEBUG:
        return os.environ[env_var]
    return os.environ.get(env_var, default)


class Config:
    salt = get_env('MWB_SALT', 'ChangeMe')
    hash_rounds = int(get_env('MWB_HASH_ROUNDS', '10'))
    gstore_db = get_env('MWB_DB', 'mwb')
    gstore_db_file = get_env('MWB_DB_FILE', '/data/weibo.nt')
    gstore_db_user = get_env('MWB_DB_USER', 'root')
    gstore_db_passwd = get_env('MWB_DB_PASSWD', '123456')
    ghttp_domain = get_env('MVB_DB_SERVER', 'localhost')
    ghttp_port = get_env('MVB_DB_PORT', 9000)
    jwt_secret = get_env('MVB_JWT', 'ChangeMe')
