#!/bin/bash
set -e

kind create cluster --name sem3 --config platform/kind-config.yaml
kind load docker-image apache/airflow:3.3.2 ghcr.io/mlflow/mlflow:v3.16.1 --name sem3
docker port sem3-control-plane

kubectl apply -f platform/mlflow.yaml -f platform/airflow.yaml

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 91.5.2 -n monitoring --create-namespace -f platform/monitoring-values.yaml --wait --timeout 15m
helm upgrade --install traefik traefik/traefik --version 41.6.0 -n traefik --create-namespace -f platform/traefik-values.yaml --wait

kubectl apply -f platform/ingress.yaml

kubectl get ingress -A
kubectl get pods -A