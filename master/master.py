from flask import Flask, request, jsonify
import time
from enum import IntEnum

app = Flask(__name__)



class TaskStatus(IntEnum):
    CREATED = 1
    WORKING = 2
    DONE = 3

def deployTask(n):
    taskID = str(time.time())
    return taskID

def getTask(taskID):
    status = TaskStatus.CREATED
    result = None

    return {
        'status': status,
        'result': result,
    }

@app.route('/task', methods=['POST'])
def create_task():
    n = int(request.form.get('n'))
    task_id = deployTask(n)
    
    return jsonify({'task_id': task_id}), 202

@app.route('/task/<task_id>', methods=['GET'])
def get_task(task_id):
    task = getTask(task_id)

    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(task), 200

if __name__ == '__main__':
    app.run(debug=True)
