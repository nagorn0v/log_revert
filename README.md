# Log and revert
The implementation of logging and revert changes.

# Requirements
**Docker-compose** (mine v2.3.3) - for local deploy

**Postman** - for requestes

# Deploy
`docker-compose build`

`docker-compose up -d`

# Tests
`docker exec -it backend bash` - enter the shell

`python tests.py` - run unittest


# Requests
The Requests are stored in **postman collection**

I am implemented simple authorization that use header **X-USER-ID** for check if user valid (correct id is 1)

## Folders
lists - The folder with requests for lists table

tasks - The folder with requests for tasks table

action - The folder with requests for user actions: get list of user's actions and undo last action

other requests - The folder with requests for several changes by one request
