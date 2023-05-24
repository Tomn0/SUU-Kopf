import time
from flask import Flask
import os
from apscheduler.schedulers.background import BackgroundScheduler
import random
from state import State
import jsonpickle

# env var init and global vars
id = os.environ.get('ID', None)
if id is None:
    print('Id env var not found in env!')

state = os.environ.get('STATE', None)
if state is None:
    state = 0
else:
    state = jsonpickle.decode(state).somenumber

salt = random.randint(1, 9999999) # random salt to generare a unique backup file name

# flask init
app = Flask(__name__)

# background task init
def bg_task():
    global state
    while True:
        state += 1
        time.sleep(5)

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(bg_task)
scheduler.start()

# flask endpoints
@app.route("/increment")
def increment():
    global state
    state += 1
    return str(state)

@app.route("/debug")
def debug():
    return str(state)

@app.route("/save")
def save():
    global id, state

    # create directory for this worker
    path = f'/usr/share/pvc/{id}'
    if not os.path.exists(path):
        os.makedirs(path)

    # save state to file
    with open(f'{path}/{salt}.dat', 'w') as file:
        state_string = jsonpickle.encode(State(state))
        file.write(f'{state_string}')

    return 'State saved correctly'
