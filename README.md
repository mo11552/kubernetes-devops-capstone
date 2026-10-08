# CloudTask Kubernetes DevOps Capstone

CloudTask is a three-tier task-management application deployed on Kubernetes. It demonstrates containerization, persistent storage, service discovery, ingress routing, health checks, scaling, rolling updates, Kustomize, and Helm.

## Architecture

```text
Browser
   |
NGINX Ingress
   |
   +-- Frontend Service --> NGINX Frontend Pods
   |
   +-- API Service ------> Flask API Pods
                                |
                         PostgreSQL Service
                                |
                     PostgreSQL StatefulSet
                                |
                       Persistent Volume
```

## Technology Stack

- Docker
- Kubernetes
- Kind
- Kubectl
- Kustomize
- Helm
- NGINX
- Python and Flask
- PostgreSQL

## Features

- Three-tier containerized application
- REST API for creating, viewing, updating, and deleting tasks
- PostgreSQL persistent storage
- Kubernetes Deployments and StatefulSet
- Internal service discovery
- NGINX Ingress routing
- Liveness and readiness probes
- CPU and memory requests and limits
- Horizontal scaling
- Pod self-healing
- Rolling updates and rollbacks
- Kustomize deployment configuration
- Reusable Helm chart

## Repository Structure

```text
.
├── app
│   ├── backend
│   └── frontend
├── helm
│   ├── cloudtask
│   └── packages
├── kind
└── manifests
    └── base
```

## Prerequisites

Install the following tools:

- Docker Desktop
- kubectl
- Kind
- Helm

## Create the Kind Cluster

```bash
kind create cluster --config kind/kind-config.yaml
kubectl get nodes
```

## Build the Application Images

```bash
docker build -t cloudtask-api:v1 app/backend
docker build -t cloudtask-frontend:v1 app/frontend
```

Load both images into the Kind cluster:

```bash
kind load docker-image cloudtask-api:v1 --name devops-capstone
kind load docker-image cloudtask-frontend:v1 --name devops-capstone
```

## Install the NGINX Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=Ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s
```

## Deploy with Kustomize

```bash
kubectl apply -k manifests/base
kubectl get all -n cloudtask
kubectl get ingress -n cloudtask
```

Open the application at:

```text
http://localhost:8088
```

## Verify the API

```bash
curl http://localhost:8088/api/tasks
curl http://localhost:8088/health
curl http://localhost:8088/ready
```

## Helm Chart

Validate the chart:

```bash
helm lint helm/cloudtask
helm template cloudtask helm/cloudtask
```

Test a custom API replica count:

```bash
helm template cloudtask helm/cloudtask \
  --set api.replicaCount=3
```

Install the chart:

```bash
helm install cloudtask helm/cloudtask
```

Upgrade the release:

```bash
helm upgrade cloudtask helm/cloudtask \
  --set api.replicaCount=3
```

Remove the Helm release:

```bash
helm uninstall cloudtask
```

The packaged chart is located at:

```text
helm/packages/cloudtask-0.1.0.tgz
```

## Kubernetes Operations Demonstrated

This project was tested for:

- Persistent PostgreSQL data
- Pod deletion and automatic recovery
- Deployment scaling
- Rolling image updates
- Deployment rollback
- Service-to-service communication
- Ingress routing
- Helm value overrides

## Cleanup

Delete the application:

```bash
kubectl delete -k manifests/base
```

Delete the Kind cluster:

```bash
kind delete cluster --name devops-capstone
```

## Security Note

The PostgreSQL password included in this project is intended only for local demonstration. Production deployments should use an external secret-management system and should not store real credentials in source control.