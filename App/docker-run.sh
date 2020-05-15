#!/usr/bin/env bash

set -e

app="flask-ringring"

echo "Running docker file in interactive mode with port forwarding (for MacOS)..."
docker run -it --rm -p 5000:5000 --name=${app} ${app}