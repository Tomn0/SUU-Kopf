# [REMOVE] According to kopf docs we shouldn't name operators "operator.py"
# This is just a minimal operator, should be replaced by a proper program

import kopf
import logging

@kopf.on.create('rsac')
def create_fn(status, **kwargs):
    logging.info(f"A create handler is called")

