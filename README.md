# SUU-Kopf

## Documentation 
Link: https://docs.google.com/document/d/1SCPIphExCSgPyzVSVte-SpKaohGpQ60DTffhRnEePMg/edit?usp=sharing

## Project Structure
- /deployment - yaml files for kubernetes deployments
  - /operator - yaml files for deploying the operator
  - /crd - yaml files for deploying the custom resource definition
  - /example - yaml files for deploying an example deployment showcasing our project
- /infrastructure - infrastructure-as-code defintions 
  - /scripts - scripts for managing the deployment and lifecycle of resources in Azure
- /master - python code for the master image
- /worker - python code for the worker image
- /operatror - python code for the operator

## Running the project

This project can be run in three ways described below:
- Locally with minikube
- Locally with minikbe for development purposes
- In the cloud on Azure

## Running locally with minikube
Prerequisites: Docker, Minikiube

1. Start minikube: `minikube start`
2. Apply the operator: `kubectl apply -f .\deployments\operator\`
3. Apply the custom resource definition: `kubectl apply -f .\deployments\crd\`
4. Apply the example deployment: `kubectl apply -f .\deployments\example\`

Now you can use `kubectl` or `minikube dashboard` to monitor the deployment.

Deleting the deployment:

1. Delete the resources: `kubectl delete -f .\deployments\example`
2. Delete the custom resource definition: `kubectl delete -f .\deployments\crd`
3. Delete the operator: `kubectl delete -f .\deployments\operator\`
4. Delete minikube: `minikube delete`

## Running locally for active development purposes
Prerequisites: Docker, Minikiube

The deployment files look for the required images on dockerhub, when developing locally we want to prevemnt that so we need to uncomment `imagePullPolicy: Never` from deployemnt yamls. This way kubernetes will use local images we'll build while developing locally.

1. Start minikube: `minikube start`

After doing changes to python files:

2. Invoke a shell inside minikube:
    - Windows (powershell): `& minikube -p minikube docker-env --shell powershell | Invoke-Expression`
    - Windows (cmd): `@FOR /f "tokens=*" %i IN ('minikube -p minikube docker-env --shell cmd') DO @%i`
    - Linux/MacOS: `eval $(minikube docker-env)`

3. In the same shell build the changed images (takes a while for the first time): 
    1. Operator: `docker build --tag suukopfproject/rsacracker .\operator\`
    2. Master: `docker build --tag suukopfproject/master .\master\`
    3. Worker: `docker build --tag suukopfproject/worker .\worker\`
4. Apply the operator: `kubectl apply -f .\deployments\operator\`
4. Apply the custom resource definition: `kubectl apply -f .\deployments\crd\`
5. Apply the example deployment: `kubectl apply -f .\deployments\example`

Use `kubectl` or the dashboard `minikube dashboard` to monitor the resources and get access to logs.

*TODO (maybe we should automate steps 2-6 ?)*

When we're ready to release new versions we can publish the images with these steps:
1. Log in to the account asssociated with this project (credentials are not publicly distributed): `docker login`
2. Build the images as per steps 2-3 above
3. Push the images
    - Operator: `docker push suukopfproject/rsacracker`
    - Master: `docker push suukopfproject/master`
    - Worker: `docker push suukopfproject/worker`

Deleting the deployment:

1. Delete the resources: `kubectl delete -f .\deployments\example`
2. Delete the custom resource definition: `kubectl delete -f .\deployments\crd`
3. Delete the operator: `kubectl delete -f .\deployments\operator\`
4. Delete minikube: `minikube delete`

## Running in Azure

**NOTE won't work yet as the scripts are not ready (TODO)**

Prerequisites: AZ CLI, An Azure subscription with sufficient funds 

*Disable minikube before attemting to prevent issues with conflicting `kubectl` configs*

Deploying the infrastructure:

1. In your terminal authenticate to your Azure account: `az login`
2. In case you use multiple Azure subscription set the desired one with: `az account set --subscription YOUR_SUBSCRIPTION`
2. Deploy the infrastructure with `./infrastructure/scripts/deploy`

Deploying the example deployment:

1. Apply the operator: `kubectl apply -f .\deployments\operator\`
2. Apply the custom resource definition: `kubectl apply -f .\deployments\crd\`
3. Apply the example deployment: `kubectl apply -f .\deployments\example`

Now you can use `kubectl` or `minikube dashboard` to monitor the deployment.

Deleting the deployment:

1. Delete the resources: `kubectl delete -f .\deployments\example`
2. Delete the custom resource definition: `kubectl delete -f .\deployments\crd`
3. Delete the operator: `kubectl delete -f .\deployments\operator\`
4. Delete minikube: `minikube delete`

Deleting the infrastructure:
1. Run `./infrastructure/scripts/teardown`
