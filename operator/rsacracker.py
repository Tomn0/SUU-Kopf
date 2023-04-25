# [REMOVE] According to kopf docs we shouldn't name operators "operator.py"
# This is just a minimal operator, should be replaced by a proper program

import kopf
import logging

@kopf.on.create('rsac')
def create_fn(status, **kwargs):
    logging.info(f"A create handler is called")

@kopf.on.create("pod", labels={ 'mylabel': 'temp-worker' })
def create_temp_worker(status, **kwargs):
    logging.info(f"TEMP worker created")

'''
TODO:
[] napisać yaml z workera
[] odpalić yamle z workerami jako 3 osobne deploymenty
[] operator on_create wykrywa powstanie workerów
[] dobić się do workerów
[] 
'''