import argparse
import asyncio
from curses.ascii import NL
import functools
import json
import os
from attr import field
import pandas
import aiohttp
import requests
import google.protobuf.descriptor_pb2 as pb2
import re
from typing import Dict, List, Iterable, Tuple



MAX_CONNECTIONS = 20
TIMEOUT = 60
STENCIL_NAMESPACE="gojek"
STENCIL_SCHEMA = "clickstream"

# Types used to parse comments
TYPE_MESSAGE = 2
TYPE_FIELD = 4
STENCIL_SEARCH = False

CONFIG = {}

def parse_args():
    parser = argparse.ArgumentParser(description='recommend proto messages for a given field')
    parser.add_argument('--f', metavar='input-file', type=str,
                    help='input csv which contains property data', dest='property_file', required=True) 
    col_ctx_group = parser.add_mutually_exclusive_group(required=True)
    col_ctx_group.add_argument('--ctx-col', metavar='property-context-column-name', type=str, dest='property_ctx_col_name',
                    help='column name in the input csv sheet which has the context for the property name to be searched')
    col_ctx_group.add_argument('--ctx-col-num', metavar='property-context-column-num', type=int,
                    help='column number in the input csv which has the context of property name to be searched',
                    dest='property_ctx_col_num')
    col_group = parser.add_mutually_exclusive_group()
    col_group.add_argument('--col', metavar='property-column-name', type=str, dest='property_col_name',
                    help='column name in the input csv sheet which has the property names to be searched')
    col_group.add_argument('--col-num', metavar='property-column-num', type=int,
                    help='column number in the input csv which has the property names to be searched',
                    dest='property_col_num')
    parser.add_argument('--out-msg-col', metavar='output-msg-column-name', type=str, default='Recommended Protos', dest='output_msg_column_name', 
                    help='output column name where recommended proto message names are filled')
    parser.add_argument('--out-field-col', metavar='output-fieldcolumn-name', type=str, default='Recommended Fields', dest='output_field_column_name', 
                    help='output column name where recommended proto fields/property names are filled')                    
    parser.add_argument('--stencil-host', type=str, default='stencil-beta.golabs.io', help=argparse.SUPPRESS, dest='stencil_host')
    parser.add_argument('--stencil-port', type=int, default=443, help=argparse.SUPPRESS, dest='stencil_port')
    parser.add_argument('--stencil-request-scheme', type=str, default='https', help=argparse.SUPPRESS, dest='stencil_request_scheme')
    parser.add_argument('--ctx-keys-del', metavar='context_keys_delimeter', type=str, dest='context_keys_delimeter',
                    help='delimeter for context keys column', default=' ')
    
    return parser.parse_args()

def get_stencil_headers() -> Dict:
    token: str = os.environ['HOFUND_STENCIL_TOKEN']
    return {'Authorization': 'Bearer {}'.format(token)} if token != "" else {}

async def stencil_search(url: str, session: aiohttp.ClientSession) -> Tuple[List]:
    try:
        async with session.get(url, headers=get_stencil_headers(), ssl=False) as resp:
            if resp.status != 200:
                print('search request failed for {}'.format(url))
                return ([], [])
            resp: bytes = await resp.read()
            resp_body = json.loads(resp)
            return (functools.reduce(lambda fields, hit: fields.union(set(hit['fields'])), resp_body['hits'], set()), 
                    functools.reduce(lambda messages, hit: messages.union(set(hit['types'])), resp_body['hits'], set())) if resp_body['meta']['total'] > 0 else ([], [])
    except Exception as e:
        print('Unable to get {} due to {}: {}'.format(url, e.__class__, e))
        return ([], [])

def get_stencil_url(stencil_request_scheme: str,
                        stencil_host: str,
                        stencil_port: str) -> str:
    return '{}://{}:{}/v1beta1'.format(
                            stencil_request_scheme, 
                            stencil_host, 
                            stencil_port)

def get_stencil_search_file_url(stencil_request_scheme: str,
                            stencil_host: str,
                            stencil_port: str) -> str:
    return '{}/namespaces/{}/schemas/{}'.format(get_stencil_url(stencil_request_scheme,
                                                   stencil_host,
                                                   stencil_port),
                                                   STENCIL_NAMESPACE,
                                                   STENCIL_SCHEMA)

def get_stencil_search_url(stencil_request_scheme: str,
                        stencil_host: str,
                        stencil_port: str,
                        query: str) -> str:
    return '{}/search?query={}&namespace_id={}&schema_id={}'.format(get_stencil_url(stencil_request_scheme,
                                                   stencil_host,
                                                   stencil_port),
                                                   query,
                                                   STENCIL_NAMESPACE,
                                                   STENCIL_SCHEMA) 

def search_comments(search_map: Dict, search_terms : List) -> str:
    items: List = []
    for s in search_terms:
        for comment, val in search_map.items():    
            s = re.sub(r"[^a-zA-Z0-9]", "", s)
            if len(s) <= 2:
                continue

            if  re.search('[A-Z0-9_\-\.]+\.\w*'+s+'w*', val, re.IGNORECASE):
                items.append(val)
            elif re.search(s, comment) and val != "google.protobuf.Timestamp":
                items.append(val)
    
    return ', '.join(items)

def search_in_map(search_terms: List[str], search_map: Dict) -> Tuple[List]:
    return search_comments(search_map['messages'], search_terms), search_comments(search_map['fields'], search_terms)


async def search(search_terms: List[str], search_map: Dict) -> Tuple[List]:
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[stencil_search(get_stencil_search_url(
            CONFIG.stencil_request_scheme,
            CONFIG.stencil_host,
            CONFIG.stencil_port,
            query), session) for query in search_terms])
        
        fields: str = ', '.join(functools.reduce(lambda x, y : x + list(y[0]), ret, []))
        messages: str =  ', '.join(functools.reduce(lambda x, y : x + list(y[1]), ret, []))

        return fields if len(fields.strip()) > 0 else search_comments(search_map['fields'], search_terms), messages if len(messages.strip()) > 0 else search_comments(search_map['messages'], search_terms)


def get_context_keys(context_str: str) -> List[str]:
    return [s.strip() for s in context_str.strip().split(CONFIG.context_keys_delimeter)] if not pandas.isna(context_str) else []


def get_searchable_terms(row: pandas.Series) -> List[str]:
    search_terms: List[str] = []


    if CONFIG.property_ctx_col_name is not None:
        search_terms += get_context_keys(row[CONFIG.property_ctx_col_name])
    else:
        search_terms += get_context_keys(row.values[CONFIG.property_ctx_col_num - 1])
    
    if CONFIG.property_col_name is not None:
        search_terms.append(row[CONFIG.property_col_name])
    elif CONFIG.property_col_num is not None:
        search_terms.append(row.values[CONFIG.property_col_num - 1])
    
    return search_terms



async def search_rows(rows: Iterable[pandas.Series], search_map: Dict) -> Tuple:
    messages: List[str] = []
    fields: List[str] = []
    for _, row in rows:
        search_res = await search(get_searchable_terms(row), search_map)
        messages.append(search_res[1])
        fields.append(search_res[0])
    return (messages, fields)

def get_comment(locations, type):
    while True:
        if len(locations) == 0:
            break
        location = locations.pop(0)
        if type == TYPE_MESSAGE:
            if len(location.path) == type and location.path[0] == 4:
                return location.leading_comments
            elif len(location.path) > type:
                return ""
            else:
                continue
        else:
            if len(location.path) == type and location.path[0] == 4:
                return location.leading_comments
            else:
                continue 

def get_proto_descriptor() -> pb2.FileDescriptorSet:
    try:
        url: str = get_stencil_search_file_url(CONFIG.stencil_request_scheme,
            CONFIG.stencil_host,
            CONFIG.stencil_port)
        res: requests.Response = requests.get(url=url, headers=get_stencil_headers())
        if res.status_code != 200:
            print('request failed for url: {}'.format(url))
        descrptor_set = pb2.FileDescriptorSet()
        descrptor_set.ParseFromString(res.content)
        return descrptor_set
    except Exception as e:
        print('Error while requesting stencil, {}:{}'.format(e.__class__, e))
        exit(1)

def search_rows_map(rows: Iterable[pandas.Series], search_map: Dict) -> Tuple:
    messages: List[str] = []
    fields: List[str] = []
    for  _, row in rows:
        search_terms = get_searchable_terms(row)
        m, f = search_in_map(search_terms, search_map) 
        messages.append(m)
        fields.append(f)
    return (messages, fields)


def get_search_map() -> Dict:
    search_map: Dict = {'messages': {}, 'fields': {}}
    descriptor_set: pb2.FileDescriptorSet = get_proto_descriptor()
    for file in descriptor_set.file:
        info = file.source_code_info
        locations = info.location
        messages = file.message_type
        for m in messages:
            comment = get_comment(locations, TYPE_MESSAGE)
            message_full_name = file.package + '.' + m.name
            search_map['messages'][message_full_name] = message_full_name
            if comment is not None and comment != "":
                search_map['messages'][comment] = message_full_name
            for f in m.field:
                field_full_name = file.package + '.' + m.name + '.' + f.name
                comment = get_comment(locations, TYPE_FIELD)
                search_map['fields'][field_full_name] = field_full_name
                if comment is not None and comment != "":
                    search_map['fields'][comment] = file.package + '.' + m.name + '.' + f.name
    return search_map
    

async def start():
    try:
        search_map: Dict = get_search_map() 
        df: pandas.DataFrame = pandas.read_csv(CONFIG.property_file)
        if STENCIL_SEARCH:
            df[CONFIG.output_msg_column_name], df[CONFIG.output_field_column_name] = await search_rows(df.iterrows(), search_map)
        else:
            df[CONFIG.output_msg_column_name], df[CONFIG.output_field_column_name] =  search_rows_map(df.iterrows(), search_map)
        df.to_csv(CONFIG.property_file, index=False)
    except Exception as e:
        print(e)

def main():
    global CONFIG
    CONFIG = parse_args()
    asyncio.run(start())

if __name__ ==  "__main__":
    CONFIG = parse_args()
    asyncio.run(start())
