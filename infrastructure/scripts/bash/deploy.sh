# AZ CLI is required
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

az group create -l uksouth -n suu-rg
az deployment group create --resource-group suu-rg --template-file ./infrastructure/main.bicep --parameters ./infrastructure/parameters.json
az aks get-credentials --resource-group suu-rg --name suu-aks
kubectl get nodes

# Wait for the node status to reach "Ready"