import time
from flask import Flask
import os
from apscheduler.schedulers.background import BackgroundScheduler

# env var init and global vars
id = os.environ.get('ID', None)
if id is None:
    print('Id env var not found in env!')
state = 0

# flask init
app = Flask(__name__)

# background task init
def bg_task():
    global state
    while True:
        state += 1
        time.sleep(5) # yeah, we should avoid this, TODO

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
    global id
    f = open(f'/usr/share/pvc/{id}.dat', 'w')
    f.write(f'{state}')
    f.close()
    return 'State saved correctly'
