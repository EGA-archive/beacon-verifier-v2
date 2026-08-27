# Beacon verifier v2

This repository contains the new Beacon verifier v2.0, a software created with the main goal of validating beacon responses against the official [GA4GH Beacon v2 specifications]((https://github.com/ga4gh-beacon/beacon-v2) ) for its debugging and testing.
The outcome of executing this tool will be a dateiled response with all the validations for each of your beacon endpoints explaining the possible errors encountered, if any.

## Installation guide with docker

Remember that you have an instance of Beacon verifier v2 in this official [link](https://beacon-verifier-demo.ega-archive.org).
First of all, clone or download the repository to your computer:
```bash
git clone https://github.com/EGA-archive/beacon-verifier-v2.git
```

Add an .env file inside the folder [verifierweb](https://github.com/EGA-archive/beacon-verifier-v2/blob/main/ui_image.png), with the next variables:
```bash
SECRET_KEY="your_django_secret_key"
CLIENT_ID='your_client_id'
SERVER_NAME=localhost
REDIRECT_URI='http://localhost:8000/oidc/my-server/login/callback/'
DJANGO_ALLOWED_HOSTS=*
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=hello_django
SQL_USER=hello_django
SQL_PASSWORD=hello_django
SQL_HOST=db
SQL_PORT=5432
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin
CELERY_BROKER=amqp://admin:admin@rabbitmq:5672/
CELERY_BACKEND=redis://redis:6379/0
CELERY_FLOWER_USER=admin
CELERY_FLOWER_PASSWORD=admin
CHANNELS_REDIS=redis://redis:6379/0
```

We *STRONGLY RECOMMEND* to modify the variable SECRET_KEY. To generate a safe Django SECRET_KEY and copy it to .env file, you can install python django package with pip install Django and generate yours with a script like this:
```bash
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```

To light up the containers with beacon verifier v2 for development environment, execute the next command inside the root folder (where docker-compose is located at):
```bash
docker-compose up -d --build
```

To light up the containers for production, execute the next command:
```bash
docker compose -f docker-compose.prod.yml -p django-celery-prod up -d --build
```

Once the container is up and running you can start using beacon verifier v2, congratulations!

## How to use verifier

### Tutorial for using verifier in your browser

Please, open the verifier UI in your browser going to http://localhost:8000 (dev environment deployment) or http://localhost:3015 (production environment deployment).

The Verifier has four steps that need to be followed in order to configurate how you want to verify your beacon.

#### Step 1. Settings

![Settings](https://github.com/EGA-archive/beacon-verifier-v2/blob/develop/staticfiles/verifier1.png)

1. Introduce yor URL in the text area after *Beacon URL*. The URL needs to be the one pointing to the root URL that preceeds the endpoint names (/datasets, /individuals, etc...) without trailing slash. For example, if your beacon has the url `www.example.com/api/datasets`, the URL you need to insert is `www.example.com/api`.

2. Set the Response Type (multiple choices allowed). Choose between HIT (only datasets with positive results), MISS (only datasets with negative results), ALL (all datasets, either with positive or negative results) or/and NONE (results not splitted per dataset).

3. Set the Granularity (multiple choices allowed). Choose what granularity do you want to verify for your beacon, all the detailed response (records), just the number of results obtained (count) and/or the response where a true/false is returned for a query (boolean).

4. Set the TestMode on or off. This is for activating your beacon in TestMode (if you have it implemented), so only the datasets meant for this mode will be returned in response.

*Note: if you choose NONE and record, the verification won't be able to be performed, as they can't be selected together. If you choose NONE, record and others, then, the verification will be performed but skipping the combination of NONE + record.*

#### Step 2. Endpoints

![Endpoints](https://github.com/EGA-archive/beacon-verifier-v2/blob/develop/staticfiles/verifier2.png)

A bunch of endpoints will load coming from the /map endpoint of your beacon. You can choose the ones you want to verify by checking them out or not. Note that /info endpoint is recommended to show the confirmation of the beacon you are verifying.

#### Step 3. Datasets

![Datasets](https://github.com/EGA-archive/beacon-verifier-v2/blob/develop/staticfiles/verifier3.png)

If there are any datasets in your beacon, the list will be showing here. You can choose whatever number of datasets you want to verify in this step, so the verification is only for the specific datasets you want. 

*Note: if you chose NONE for Response Type in Step 1, this Step 3 will be skipped for obvious reasons.*

#### Step 4. Summary

![Summary](https://github.com/EGA-archive/beacon-verifier-v2/blob/develop/staticfiles/verifier4.png)

Here you will get the table with all the options you selected before. You can now start verification by pressing Start and you will go to the *Displaying the results of the verification* stage.

#### Displaying (and understanding) the results of the verification

You can stop verification at any time by pressing the button Stop.

At the right side of the interface, you will see the different validation snippets for each of the endpoints:

![Results](https://github.com/EGA-archive/beacon-verifier-v2/blob/develop/staticfiles/verifier5.png)

- If the endpoint verified is correct, you will see the box for the snippet in green with a check.

- If the endpoint verified is incorrect because a problem in the schema, you will see the box in orange with an exclamation mark in a triangle. You will be able to see the dataset (in case it doesn't belong to a NONE response), the response type and granularity for which the endpoint is failing. You will be able to drop down the expected schema and the received response.

- If the endpoint verified is incorrect due to a server error that couldn't deliver a 200 response, you will se the box in red with a cross.

#### Downloading results

When validation finishes, because of it being stopped manually or because it fully reach completion, you will be able to download a .txt file with all the snippets collected, by clicking the Download Report button next to the Results Summary table.

![Download](https://github.com/EGA-archive/beacon-verifier-v2/blob/develop/staticfiles/verifier6.png)

The Results Summary table will give you the number for each type of resulting verification case of the endpoints.

### Alternatively, execute minimalistic verifier using the console/terminal

The full featured verifier is only available by UI. There is a minimalistic script that does a very generic validation of the API framework through the terminal.

If you wish to use the verifier using the console/terminal of your computer, please, open a prompt for your computer and type the next command replacing the url for the one containing the beacon you want to validate:

```bash
docker exec verifier python verifier.py -url http://beacon:5050/api
```
