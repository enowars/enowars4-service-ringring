#!/usr/bin/env sh

# DroneCI does not wait for services (or `detach: true` steps) to start up completely before continuing with other steps.
# However, for the tests it is required that all services are up & running
echo -e "\e[32m\nEnsuring all services are running before starting tests...\e[0m"

sleep 5
until [ "`docker inspect -f {{.State.Running}} $(docker ps --filter ancestor=localhost:5000/ringring-service -q)`"=="true" ]; do sleep 0.1; done;
until [ "`docker inspect -f {{.State.Running}} $(docker ps --filter ancestor=localhost:5000/ringring-service-postgres -q)`"=="true" ]; do sleep 0.1; done;

while [ 1 ]; do
    nc -vz ringring:7353
    if [ $? = 0 ]; then break; fi;
    sleep 1s;
done;
echo -e "\e[32m\nService up & running...\e[0m"

while [ 1 ]; do
    nc -vz postgres:5432
    if [ $? = 0 ]; then break; fi;
    sleep 1s;
done;
echo -e "\e[32m\nPostgres up & running...\e[0m"
