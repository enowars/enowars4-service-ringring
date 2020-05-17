#!/usr/bin/env bash

set -e

app="flask-ringring"
db="postgres"

docker rm -f $db | echo 'Container $db already stopped and removed.'
docker rm -f $app | echo 'Container $app already stopped and removed.'


echo -e "\e[32m\nBuilding Dockerfiles...\e[0m"
docker build -t $app -f App/Dockerfile .
docker build -t $db -f Postgres/Dockerfile .

echo -e "\e[32m\nStarting containers...\e[0m"
docker run -d -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=ringring -e POSTGRES_DB=service --name=$db $db
docker run -d -e PGPASSWORD=mysecretpassword -e PGHOST=postgres -p 7353:7353 --name=$app $app

echo -e "\e[32m\nSetting up container networking...\e[0m"
docker network rm ring
docker network create ring
docker network connect ring flask-ringring
docker network connect ring postgres

echo -e "\e[32m\nFlask app logs...\e[0m"
docker logs --follow $app