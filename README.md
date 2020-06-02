# ringring
*ringring* is a hotel room service chat bot. <br>
Currently, the user can set an alarm, order food or pay his open invoices by communicating with the bot. 
A second service keeps track of proper invoicing, allowing the user to either pay direclty while ordering
the service or to put the amount due on his room bill.

## Documentation
- Two Python Flask Apps ([Main App](App) and [Invoice App](InvoiceApp)) with one [Postgres database](Postgres) as backend.
- Currently two vulnerabilities
    - One inside the main app (look at Postgres)
    - One inside the invoice app (look at the logging)
   
- The two separate Apps are needed to ensure that both vulnerabilities can be exploited independent of each other.
- Services are orchestrated as three docker containers with only the main app being publically accessible. The Invoice 
App should only be reachable from the Main App. To run locally execute `docker-run.sh`. This will build all necessary 
containers and networks. 
- The app is designed to be build by a droneCI server, therefore the `.drone.yml` file replaces the docker-compose file.
- Integration tests (pytests) can be found [here](integration-tests/). To run them, execute `integration-test/run-locally.py`.
 
