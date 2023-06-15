import time
import sys
from flask import Flask
import os
from apscheduler.schedulers.background import BackgroundScheduler
import random
from state import State, create_initial_state
import jsonpickle
import logging

# env var init and global vars
id = os.environ.get('ID', None)
if id is None:
    print('Id env var not found in env!')

state = os.environ.get('STATE', None)
if state is None:
    state = create_initial_state()
else:
    state = jsonpickle.decode(state)

salt = random.randint(1, 9999999) # random salt to generare a unique backup file name

# flask init
app = Flask(__name__)

# set logs to sys.stdout
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

# flask endpoints
@app.route("/increment")
def increment():
    global state
    state.current_number += 1
    return str(state)

@app.route("/debug")
def debug():
    return str(state)

@app.route("/save")
def save(solution=False):
    global id, state

    # create directory for this worker
    path = f'/usr/share/pvc/{id}'
    if not os.path.exists(path):
        os.makedirs(path)

    if solution:
        with open(f'{path}/solution.dat', 'w') as file:
            state_string = jsonpickle.encode(state)
            file.write(f'{state_string}')

    # save state to file
    with open(f'{path}/{salt}.dat', 'w') as file:
        state_string = jsonpickle.encode(state)
        file.write(f'{state_string}')

    return 'State saved correctly'

# background task init
def bg_task():
    global state
    
    while state.current_number <= state.last_number:
        # print(f"print: Trying number: {state.current_number}")
        # logging.info(f"Trying number: {state.current_number}")
        if state.N % state.current_number == 0:
            state.solution = state.current_number
            # print(f"print: Found solution {state.solution}")
            # logging.info(f"Found solution {state.solution}")
            save(solution=True)
            return
        state.current_number += 1

    
    save()

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(bg_task)
scheduler.start()

