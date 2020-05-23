#!/usr/bin/env bash

set -e

if [[ $(docker inspect -f '{{.State.Running}}' registry) != 'true' ]]; then
    docker network create registry-network
    docker run -d -p 5000:5000 --restart=always --net=registry-network --name registry registry:2
fi

drone exec .drone.yml --trusted --exclude trigger-vm-image-creation --include publish-docker-invoices