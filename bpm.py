#! /usr/bin/env python

import os
import json

from bottle import run, route, request, response, HTTPResponse, HTTPError
from omhe.core.parseomhe import parseomhe

if 'BPM_SECRET_KEY' not in os.environ:
    raise ValueError('BPM_SECRET_KEY not set')
if 'BPM_DATA_PATH' not in os.environ:
    raise ValueError('BPM_DATA_PATH not set')
if 'BPM_HOST' not in os.environ:
    raise ValueError('BPM_HOST not set')

secret = os.environ['BPM_SECRET_KEY']
persist_path = os.environ['BPM_DATA_PATH']
parser = parseomhe()

# load previous data if any
data = []
if os.path.exists(persist_path):
    with open(persist_path, 'r') as ip:
        for line in ip:
            data.append(json.loads(line))

def authorized(key):
    return key == secret

@route('/update')
def update():
    if not authorized(request.query.key):
        raise HTTPError(status=403)
    value = parser.parse(request.query.value)
    if 'error' in value:
        # omhe parser doesn't raise exception, but inserts 'error'
        raise HTTPError(status=400)
    data.append(value)
    with open(persist_path, 'a') as op:
        op.write("%s\n" % json.dumps(value))
    return 'ok'

@route('/dump')
def dump():
    if not authorized(request.query.key):
        raise HTTPError(status=403)
    response.content_type = 'application/json'
    return json.dumps(data)

if __name__ == '__main__':
    run(host=os.environ['BPM_HOST'], port=int(os.environ.get('BPM_PORT', '8080')))
