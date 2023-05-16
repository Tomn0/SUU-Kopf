# [REMOVE] According to kopf docs we shouldn't name operators "operator.py"
# This is just a minimal operator, should be replaced by a proper program

import kopf
import logging
import asyncio
from state import State
from requests import Session
import kubernetes


state_registry = {}

@kopf.on.create('rsac', retries=1)
def create_fn(status, **kwargs):
    logging.info(f"A create handler is called")

@kopf.on.create("pod", labels={ 'application': 'rsac-worker' }, retries=1)
def pod_on_create(meta: kopf.Meta, **kwargs):
    global state_registry

    id = meta.labels.get('rsac-id')

    if state_registry.get(id, None) is not None:
        logging.info(f'This pod has state which needs to be restored: {state_registry[id]}')

    state_registry[id] = State(0)

    api = kubernetes.client.CoreV1Api()
    api.delete_namespaced_pod(meta.name, meta.namespace)

@kopf.on.delete("pod",labels={ 'application': 'rsac-worker' }, retries=1)
def pod_on_delete(meta: kopf.Meta, **kwargs):
    global state_registry

    id = meta.labels.get('rsac-id')

    f = open(f'/usr/share/pvc/{id}.dat', 'r') # TODO handle file not found
    somenumber = int(f.readlines()[0])
    f.close()

    state_registry[id] = State(somenumber)

