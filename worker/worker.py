import time
from flask import Flask
import os

os.environ["DEAD"] = "100"

# TODO
# Code of the worker pod created by the operator
print('Hello world from the TEMP worker')


app = Flask(__name__)

state = 0
# while True:
#     state += 1
#     time.sleep(1)

state += 10

@app.route("/counter")
def save():
  return state


@app.route("/save")
def file_write():
    f = open('/usr/share/pvc/state.dat', 'a+')
    f.write(f'{state}')
    f.close()
    return 1
