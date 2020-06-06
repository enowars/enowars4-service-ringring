#!/usr/bin/env bash

set -e

app="ringring"
invoices="ringring-invoices"
db="ringring-postgres"

echo -e "\e[32m\nStopping & removing containers...\e[0m"
docker rm -f $db || echo "Container $db already stopped and removed."
docker rm -f $app || echo "Container $app already stopped and removed."
docker rm -f $invoices || echo "Container $invoices already stopped and removed."

if [[ $1 != "-s" && $1 != "--skip-build-step" ]]; then
    echo -e "\e[32m\nBuilding Dockerfiles...\e[0m"
    cd service
    docker build -t $app -f App/Dockerfile .
    docker build -t $invoices -f InvoiceApp/Dockerfile .
    docker build -t $db -f Postgres/Dockerfile .
fi

echo -e "\e[32m\nStarting containers...\e[0m"
docker run -d -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=ringring -e POSTGRES_DB=service --name=$db $db
docker run -d -p 7354:7354 --name=$invoices $invoices
docker run -d -e PGPASSWORD=mysecretpassword -e PGHOST=$db -e INVOICE_HOST=$invoices -p 7353:7353 --name=$app $app

echo -e "\e[32m\nSetting up container networking...\e[0m"
docker network rm ring 2> /dev/null || true
docker network create ring
docker network connect ring $db
docker network connect ring $app
docker network connect ring $invoices

if [[ $1 = "-f" ]]; then
    echo -e "\e[32m\nFlask app logs...\e[0m"
    docker logs --follow $app
fi