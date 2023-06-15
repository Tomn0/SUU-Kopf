import kopf
import logging
from state import State, create_initial_state, is_gte
import kubernetes
import jsonpickle
import os
import time
import yaml
import random
import math
import socket
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler




operator_directory = '/usr/share/pvc/operator' # directory in PVC where the operator keeps its files

def getOperatorIp():
    return socket.gethostbyname(socket.gethostname())

@kopf.on.create("rsac", retries=1)
def rsac_on_create(meta: kopf.Meta, spec: kopf.Spec, **kwargs):
    worker_count = spec['workerCount']
    N = spec['numberToFactor']

    api = kubernetes.client.CoreV1Api()

    last_number_to_check = int(math.sqrt(N))
    each_state_size = int(last_number_to_check / worker_count)
    states = []

    for i in range(worker_count):
        first_number = i * each_state_size
        last_number = (i+1) * each_state_size - 1

        if first_number < 2:
            first_number = 2

        states += [State(N, first_number, last_number)]
    
    states[-1].last_number = last_number_to_check

    # create workers
    for i,starting_state in enumerate(states):
        worker_id = f'id{i}'
        worker_manifest = create_worker_yaml(worker_id, starting_state)
        api.create_namespaced_pod(meta.namespace, worker_manifest)

    # this file tells the operator that it is working, deleting it will make the operator ignore the workers
    if not os.path.exists(operator_directory):
        os.mkdir(operator_directory)
    with open(os.path.join(operator_directory, 'is_working'), 'w'):
        # the contents are empty, it's just the exsitance of this file that's important to the operator
        pass
    
    # create master
    master_manifest = create_yaml('master', {
        'operator_ip': getOperatorIp(),
    })
    api.create_namespaced_pod(meta.namespace, master_manifest)

    # create user-master service
    user_master_service_manifest = create_yaml('user-master-service')
    api.create_namespaced_service(meta.namespace, user_master_service_manifest)

@kopf.on.delete("rsac", retries=1)
def rsac_on_delete(meta: kopf.Meta, **kwargs):
    api = kubernetes.client.CoreV1Api()
    
    # delete service
    api.delete_namespaced_service('user-master-service', meta.namespace)

    # delete master
    api.delete_namespaced_pod('master', meta.namespace)

    # delete the is_working file, which will cause the operator to stop caring about the workers
    if os.path.exists(os.path.join(operator_directory, 'is_working')):
        os.remove(os.path.join(operator_directory, 'is_working'))

    # find pods to be deleted
    pod_list = api.list_namespaced_pod(namespace=meta.namespace, watch=False)
    names_to_be_deleted = []
    for pod in pod_list.items:
        if pod.metadata.labels.get('rsac-id', None) is not None: # finds everyone with the 'rsac-id' label
            names_to_be_deleted.append(pod.metadata.name)

    # delete pods
    api = kubernetes.client.CoreV1Api()
    for pod_name in names_to_be_deleted:
        api.delete_namespaced_pod(pod_name, meta.namespace)

@kopf.on.update("rsac", retries=1)
def pod_on_update(meta: kopf.Meta, spec: kopf.Spec, **kwargs):
    logging.info(f'Detected update event')

    api = kubernetes.client.CoreV1Api()

    # delete old workers
    # delete the is_working file, which will cause the operator to stop caring about the workers
    if os.path.exists(os.path.join(operator_directory, 'is_working')):
        os.remove(os.path.join(operator_directory, 'is_working'))

    # find pods to be deleted
    pod_list = api.list_namespaced_pod(namespace=meta.namespace, watch=False)
    names_to_be_deleted = []
    for pod in pod_list.items:
        if pod.metadata.labels.get('rsac-id', None) is not None: # finds everyone with the 'rsac-id' label 
            names_to_be_deleted.append(pod.metadata.name)

    # delete pods
    logging.info(f'Deleting old workers: {names_to_be_deleted}')
    api = kubernetes.client.CoreV1Api()
    for pod_name in names_to_be_deleted:
        api.delete_namespaced_pod(pod_name, meta.namespace)


    worker_count = spec['workerCount']
    N = spec['numberToFactor']


    last_number_to_check = int(math.sqrt(N))
    each_state_size = int(last_number_to_check / worker_count)
    states = []

    for i in range(worker_count):
        first_number = i * each_state_size
        last_number = (i+1) * each_state_size - 1

        if first_number < 2:
            first_number = 2

        states += [State(N, first_number, last_number)]
    
    states[-1].last_number = last_number_to_check

    # create workers
    for i,starting_state in enumerate(states):
        worker_id = f'id{i}'
        worker_manifest = create_worker_yaml(worker_id, starting_state)
        api.create_namespaced_pod(meta.namespace, worker_manifest)

    # this file tells the operator that it is working, deleting it will make the operator ignore the workers
    if not os.path.exists(operator_directory):
        os.mkdir(operator_directory)
    with open(os.path.join(operator_directory, 'is_working'), 'w'):
        # the contents are empty, it's just the exsitance of this file that's important to the operator
        pass


#########################################
#########################################
#########################################

@kopf.on.create("pod", labels={ 'application': 'rsac-worker' }, retries=1)
def pod_on_create(meta: kopf.Meta, spec: kopf.Spec, **kwargs):
    if not os.path.exists(os.path.join(operator_directory, 'is_working')):
        return # the file which indicates we should be working, does not exist - don't do anything

    id = meta.labels.get('rsac-id')
    current_state = get_starter_state_from_spec(spec)
    desired_state = get_best_backup_state_for_id(id)

    if is_gte(current_state, desired_state):
        logging.info(f'A pod was created with an up-to-date state: {current_state}')
    else:
        logging.info(f'This pod has invalid state, is {current_state} should be: {desired_state}. It will be deleted!')

        api = kubernetes.client.CoreV1Api()
        api.delete_namespaced_pod(meta.name, meta.namespace)


@kopf.on.delete("pod",labels={ 'application': 'rsac-worker' }, retries=1)
def pod_on_delete(meta: kopf.Meta, **kwargs):
    if not os.path.exists(os.path.join(operator_directory, 'is_working')):
        return # the file which indicates we should be working, does not exist - don't do anything

    id = meta.labels.get('rsac-id')  

    # read the backup contents
    backup_state = get_best_backup_state_for_id(id)
    logging.info(f"A pod with id '{id}' is being deleted, the most up-to-date state for this pod is: {backup_state}")

    # create a new worker with the state of the dead worker
    logging.info(f'A new worker is created here with state: {jsonpickle.encode(backup_state)}')


    worker_manifest = create_worker_yaml(id, backup_state)
    api = kubernetes.client.CoreV1Api()
    api.create_namespaced_pod(meta.namespace, worker_manifest)

    logging.info(f'Worker pod created: in namespace: {meta.namespace}')


def create_worker_yaml(id: str | int, state: State = None, salt: int = None):
    # Defaults:
    if salt is None:
        salt = random.randint(10000, 99999) # salt is a unique rnadom number
    if state is None:
        state = create_initial_state()

    # Prepare yaml
    with open('rsac-worker.yaml', 'r') as file:
        formatted_yaml = file.read().format(
            id = id,
            salt = salt,
            state = f"'{jsonpickle.encode(state)}'"
        )
        return yaml.safe_load(formatted_yaml)

def create_yaml(yamlFilename: str, params: dict = {}):
    path = os.path.join(os.path.dirname(__file__), yamlFilename + '.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(**params)
    return yaml.safe_load(text)


def get_starter_state_from_spec(spec: kopf.Spec) -> State:
    env = spec['containers'][0]['env']
    for variable in env:
        if variable['name'] == 'STATE':
            return jsonpickle.decode(variable['value'])
    return create_initial_state()

def get_best_backup_state_for_id(id) -> State:
    # also removes all backup files with worse states than the best

    path = f'/usr/share/pvc/{id}'
    if os.path.exists(path): # this directory should exist, workers create their own directories before dying
        # find the backup file for the instance which did the most work (and delete all others)
        longest_running_state = create_initial_state()
        longest_running_file_name = None
        for file_name in os.listdir(path):
            with open(os.path.join(path, file_name)) as backup_file:
                state = jsonpickle.decode(backup_file.read())
                logging.info(f'Operator considering file: {file_name} which holds state {state}')
                if is_gte(longest_running_state, state):
                    # longest_running_state is bigger then the state in the file, discard the file
                    os.remove(os.path.join(path, file_name))
                else:
                    # the state in the file is bigger than the current best, make it the new best and remove the old file
                    if longest_running_file_name is not None:
                        os.remove(os.path.join(path, longest_running_file_name))
                    longest_running_file_name = file_name
                    longest_running_state = state
        return longest_running_state
    else:
        return create_initial_state()



# api for starting task, used by master

app = Flask(__name__)

def run_flask():
    logging.debug("Running flask...")
    app.run(host="0.0.0.0", port=8080)

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(run_flask)
scheduler.start()

@app.route('/progress', methods=['GET'])
def progress():
    logging.debug(f"Received progress request")
    
    states = []
    progress_done = 0
    progress_all = 0
    solution = None

    path = f'/usr/share/pvc'
    if os.path.exists(path):
        for id_path in os.listdir(path):
            for file_name in os.listdir(os.path.join(path, id_path)):
                file_stats = os.stat(os.path.join(path, id_path, file_name))

                if file_stats.st_size <= 0:
                    continue

                with open(os.path.join(path, id_path, file_name)) as backup_file:
                    states += [jsonpickle.decode(backup_file.read())]
    
    for state in states:
        progress_done += (state.current_number - state.first_number)
        progress_all += (state.last_number - state.first_number)

        if state.solution is not None:
            solution = state.solution
    
    return jsonify({
        'progress_done': progress_done,
        'progress_all': progress_all,
        'solution': solution
    }), 200
