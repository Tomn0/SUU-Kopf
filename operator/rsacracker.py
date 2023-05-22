import kopf
import logging
from state import State, create_initial_state, compare_state
from requests import Session
import kubernetes
import jsonpickle
import os
import yaml
import jinja2

@kopf.on.create("pod", labels={ 'application': 'rsac-worker' }, retries=1)
def pod_on_create(meta: kopf.Meta, spec: kopf.Spec, **kwargs):
    id = meta.labels.get('rsac-id')
    current_state = get_starter_state_from_spec(spec)
    desired_state = get_best_backup_state_for_id(id)

    if compare_state(desired_state, current_state):
        logging.info(f'This pod has invalid state, is {current_state} should be: {desired_state}')

        # delete the pod with invalid state - FIXME: uncomment after testing!
        # api = kubernetes.client.CoreV1Api()
        # api.delete_namespaced_pod(meta.name, meta.namespace)
        logging.info(f'Normally a pod is deleted here!')
    else:
        logging.info(f'A pod was created with an up-to-date state: {current_state}')


@kopf.on.delete("pod",labels={ 'application': 'rsac-worker' }, retries=1)
def pod_on_delete(meta: kopf.Meta, **kwargs):
    id = meta.labels.get('rsac-id')  

    # read the backup contents
    backup_state = get_best_backup_state_for_id(id)
    logging.info(f"A pod with id '{id}' is being deleted, the most up-to-date state for this pod is: {backup_state}")

    # create a new worker with the state of the dead worker
    logging.info(f'A new worker is created here with state: {jsonpickle.encode(backup_state)}')

    # Load the YAML template file
    with open('rsac-worker.yaml', 'r') as f:
        worker_manifest = yaml.safe_load(f)

    worker_manifest['metadata']['name'] = 'rsac-worker' + str(int(id)+1)
    worker_manifest['metadata']['labels']['rsac-id']  = str(int(id)+1)
    worker_manifest['spec']['containers'][0]['env'][0]['value'] = str(int(id)+1)
    worker_manifest['spec']['containers'][0]['env'][1]['value'] = str(jsonpickle.encode(backup_state))

    logging.info(f'Deploying pod with manifest: {worker_manifest}')

    api = kubernetes.client.CoreV1Api()
    namespace = meta.namespace
    api.create_namespaced_pod(namespace, worker_manifest)
    logging.info(f'Worker pod created: in namespace: {namespace}')

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
                if compare_state(longest_running_state, state):
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
