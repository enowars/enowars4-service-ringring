#!/usr/bin/env bash

set -e

app="flask-ringring"

docker build -t ${app} .