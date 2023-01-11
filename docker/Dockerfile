FROM python:3.11.0-buster
WORKDIR /code
RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip config set install.trusted-host mirrors.aliyun.com
RUN pip install pyjwt django rdflib uwsgi requests django-cors-headers
# CMD sleep 3; python3 manage.py shell -c "from backend.gstore_helpers import init_db; init_db()"; uwsgi --ini uwsgi.iniuwsgi --ini uwsgi.ini  
CMD sleep 3; python3 manage.py shell -c "from backend.gstore_helpers import init_db; init_db()"; python3 manage.py runserver 0.0.0.0:8000