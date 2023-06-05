from flask import Flask, request, jsonify
import time
import requests
from enum import IntEnum

app = Flask(__name__)

start_task_endpoint = 'htttp://10.103.170.51:80/start-task'

class TaskStatus(IntEnum):
    CREATED = 1
    WORKING = 2
    DONE = 3

def get_task(taskID):
    status = TaskStatus.CREATED
    result = None

    return {
        'status': status,
        'result': result,
    }

@app.route('/task', methods=['POST'])
def create_task():
    n = int(request.form.get('n'))

    # send start-task request to operator
    response = requests.post(start_task_endpoint, json={"n" : n})

    # return created task's id
    task_id = response.json()['task_id']
    return jsonify({'task_id': task_id}), 202

@app.route('/task/<task_id>', methods=['GET'])
def get_task(task_id):
    task = get_task(task_id)

    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(task), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
