SECRET_KEY = 'django-insecure-%7n^mr6gznjqe3^a_n8=rk-3pl-*gt2$4_)cem+5lxr75+2=a^'
DEBUG = True
ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'boot.urls'
CORS_ORIGIN_ALLOW_ALL  = True
USE_TZ = False

INSTALLED_APPS = [
    'corsheaders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware'
]
