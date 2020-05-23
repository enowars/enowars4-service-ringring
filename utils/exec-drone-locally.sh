#!/usr/bin/env bash

set -e

if [[ $(docker inspect -f '{{.State.Running}}' registry) != 'true' ]]; then
    docker network rm registry-network 2> /dev/null || true
    docker network create registry-network
    docker run -d -p 5000:5000 --restart=always --net=registry-network --name registry registry:2
fi

if [[ -z "$1" ]]; then
    drone exec .drone.yml --trusted --exclude trigger-vm-image-creation --pipeline $1
else
    drone exec .drone.yml --trusted --exclude trigger-vm-image-creation
fi