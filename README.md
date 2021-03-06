# ringring [![Build Status](https://droneci.sect.tu-berlin.de/api/badges/enowars/enowars4-service-ringring/status.svg)](https://droneci.sect.tu-berlin.de/enowars/enowars4-service-ringring)
*ringring* is a hotel room service chat bot. <br>
The user can set an alarm, order food or pay his open invoices by communicating with the bot. 
A second service keeps track of proper invoicing, allowing the user to either pay direclty while ordering
the service or to put the amount due on his room bill.

---
# The Service
## Documentation
### General
Two Python Flask Apps ([Main App](service/App) and [Invoice App](service/InvoiceApp)) with both having a dedicated Postgres database as backend. All user interaction is based on a *session_id* cookie. There is no register / login functionality required.
The Apps are being deployed as [gunicorn servers](https://gunicorn.org/) for increased reliability and performance. 
The two separate Apps and DBs are necessary to ensure that both vulnerabilities can be exploited independent of each other.
Services are orchestrated as docker containers with only the main app being publically accessible. The Invoice 
App should only be reachable from the Main App. See the [docker-compose.yml](service/docker-compose.yml) for further definitions. 

The *rotator_cron* container is used to rotate logs created by the invoice app in order to keep logfiles from growing to large (this is alos interesting / needed for the exploit to work properly).

### Vulnarabilities
Currently two vulnerabilities
- One inside the main app (look at Postgres)
- One inside the invoice app (look at the logging)
   

## Development
### Build
To build the service locally, run `docker-compose up --build` from the [service directory](/service/). The main app will be available from [port 7353](http://localhost:7353/).

### Test
Integration tests (pytests) that check most of the functionalitites can be found [here](tests/integration-tests/). 
To run them, execute `run-locally.py`. The script will take care of building your docker containers so that all necessary ports are published. It will down these containers after testing. *In case you have deployed the app before testing, you might need to up them again after the test run*. Have a look at the [docker-compose override file](tests/integration-tests/docker-compose.override.yml) to see what is changing from the standard deployment.

You can run load tests against your deployment with the tools provided in the [load-tests](/tests/load-tests) directory. Executing `run_load.py` will create multiple agents throwing multiple asycronous requests against your service. Play around with `MIN_NUMBER_OF_CONCURRENT_REQUESTS_PER_THREAD`, `MAX_NUMBER_OF_CONCURRENT_REQUESTS_PER_THREAD` and `NUMBER_OF_THREADS` to find the performance bottlenecks of your current deployment.

---
# The Checker
The checker is based on [enochecker](https://github.com/enowars/enochecker).

## Documentation
### Flagstores
The checker puts flags in two locations.
- as message to a created alarm
- as additional text to a food order

Noise is created in these same two places. 

The checker creates a new session for every action. In order for checker sessions to not be displayed on the `/guests` endpoint of the main app by default, sessions from which alarms are created are being marked as *vip sesssions*.


 
