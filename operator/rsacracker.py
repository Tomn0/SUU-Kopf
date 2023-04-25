# [REMOVE] According to kopf docs we shouldn't name operators "operator.py"
# This is just a minimal operator, should be replaced by a proper program

import kopf
import logging
import asyncio
from requests import Session

@kopf.on.create('rsac')
def create_fn(status, **kwargs):
    logging.info(f"A create handler is called")

@kopf.on.create("pod", labels={ 'mylabel': 'temp-worker' })
def create_temp_worker(status, **kwargs):
    logging.info(f"TEMP worker created")
    return 8888


@kopf.on.delete("pod", labels={ 'mylabel': 'temp-worker' })
async def handle_delete(status, **kwargs):
    # logging.info(f"This is the STATUS: {status}")
    # pod_ip = status['podIP']
    # logging.info(pod_ip)

    # session = Session()
    # result = await asyncio.get_event_loop().run_in_executor(None, session.get, f'http://{pod_ip}/counter')
    # logging.info(f"Call to restore returned with state=`{result.text}`")
    f = open('/usr/share/pvc/state.dat', 'r')
    logging.info(f.readlines())
    f.close()

