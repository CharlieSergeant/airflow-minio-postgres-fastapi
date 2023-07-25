#!/bin/bash

## Docker
echo "Initializing Project..."

sudo docker network create datastore
sudo docker volume create traefik-public-certificates
sudo docker volume create downloads

# Comment these out if you dont need them
echo "Building selenium and jupyter containers"
sudo docker build -t docker_selenium -f ./.docker/selenium/Dockerfile .
sudo docker build -t docker_jupyter -f ./.docker/jupyter/Dockerfile .

## Minio
echo "User needs to manually setup Minio instance..."
# (This will be here until we automate this)
