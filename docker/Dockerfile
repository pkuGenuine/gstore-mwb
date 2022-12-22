FROM python:3.11.0-buster
WORKDIR /code
RUN pip install pyjwt django rdflib uwsgi requests
CMD sleep 3; python3 manage.py shell -c "from backend.gstore_helpers import init_db; init_db()"; uwsgi --ini uwsgi.ini 