from flask import Flask, request, jsonify
import time
import requests
from enum import IntEnum
import os

operator_ip = os.environ.get('OPERATOR_IP', None)

if operator_ip is None:
    print('operator_ip env var not found in env!')

app = Flask(__name__)

@app.route('/')
@app.route('/progress')
def progress():
    # send start-task request to operator
    response = requests.get('http://' + operator_ip + ':8080/progress')

    return response.json(), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
