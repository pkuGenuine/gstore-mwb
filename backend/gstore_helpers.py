from typing import Dict, List, Any
import json
import re
from datetime import datetime

from rdflib import Literal

from boot.config import Config
from utils.gstore_connector import GstoreConnector

gc = GstoreConnector(Config.ghttp_domain, Config.ghttp_port,
                     Config.gstore_db_user, Config.gstore_db_passwd)


def init_db():
    gc.build(Config.gstore_db, Config.gstore_db_file)
    gc.load(Config.gstore_db, 0)


def n3literal(data: Any) -> str:
    return Literal(data).n3()


def query(sparql: str) -> Dict[str, Any]:
    def replace(matchobj):
        src: str = matchobj.group(0).strip()
        v = src[src.find(':') + 1:]
        if src.startswith(':'):
            return f' <http://fake-uri/miniweibo/volcab#{v}> '
        if src.startswith('rdf:'):
            return f' <http://www.w3.org/1999/02/22-rdf-syntax-ns#{v}> '
        if src.startswith('rdfs:'):
            return f' <http://www.w3.org/2000/01/rdf-schema#{v}> '
    # TODO: Not that good
    sparql = re.sub(r'(rdf|rdfs)?:[a-zA-Z\-]+ ', replace, sparql) # type: ignore
    print(sparql)
    result = json.loads(gc.query(Config.gstore_db, 'json', sparql)) # type: ignore
    print(result)
    return result


def to_py(data: Dict[str, str]) -> str | int | datetime:
    # TODO: Find a better way to deserialize it
    if data['type'] == 'uri':
        return f'<{data["value"]}>'
    if data['type'] == 'literal':
        return data['value']
    if data['type'] == 'typed-literal':
        if '#integer' in data['datatype']:
            return int(data['value'])
        if '#dateTime' in data['datatype']:
            try:
                return datetime.strptime(data['value'], '%Y-%m-%dT%H:%M:%S')
            except:
                return datetime.strptime(data['value'], '%Y-%m-%dT%H:%M:%S.%f')
    raise NotImplementedError


def select(vars: List[str], condition: str) -> List[List[Any]]:
    var_binding = ' '.join(['?' + v for v in vars])
    result = query('select ' + var_binding + '\n' + condition)
    return list(map(lambda binding: [to_py(binding[v]) for v in vars],
                    result['results']['bindings']))


def select_x(condition: str) -> List[Any]:
    result = query('select ?x\n' + condition)
    return list(map(lambda binding: to_py(binding['x']),
                    result['results']['bindings']))


def ask(sparql: str) -> bool:
    result = query(sparql)
    result = result['results']['bindings'][0]['_askResult']['value']
    return result == 'true'


def update(sparql: str):
    result = query(sparql)
    # TODO: Not always sync to disk
    gc.checkpoint(Config.gstore_db)
    # TODO: Clear Cache
