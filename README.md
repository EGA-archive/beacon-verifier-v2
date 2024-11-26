# Beacon verifier v2

This repository contains the new Beacon verifier v2.0, a software created with the main goal of validating beacon responses against the official [GA4GH Beacon v2 specifications]((https://github.com/ga4gh-beacon/beacon-v2) ) for its debugging and testing.
The outcome of executing this tool will be a dateiled response with all the validations for each of your beacon endpoints explaining the possible errors encountered, if any.

## Installation guide with docker

First of all, clone or download the repository to your computer:
```bash
git clone https://github.com/EGA-archive/beacon-verifier-v2.git
```

Add an .env file inside the folder [verifierweb](https://github.com/EGA-archive/beacon-verifier-v2/blob/main/ui_image.png), with the next variables:
```bash
SECRET_KEY="your_django_secret_key"
OIDC_RP_CLIENT_ID='your_client_id'
OIDC_RP_CLIENT_SECRET='your_client_secret'
```

We *STRONGLY RECOMMEND* to modify the variable SECRET_KEY. To generate a safe Django SECRET_KEY and copy it to .env file, you can install python django package with pip install Django and generate yours with a script like this:
```bash
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```

To light up the containers with beacon verifier v2, execute the next command inside the root folder (where docker-compose is located at):
```bash
docker-compose up -d --build
```

To light up the containers for production, execute the next command:
```bash
docker compose -f docker-compose.prod.yml -p django-celery-prod up -d --build
```

Once the container is up and running you can start using beacon verifier v2, congratulations!

## Excute verifier using the console/terminal

If you wish to use the verifier using the console/terminal of your computer, please, open a prompt for your computer and type the next command replacing the url for the one containing the beacon you want to validate:

```bash
docker exec verifier python verifier.py -url http://beacon:5050/api
```

## Excute verifier using the UI

Please, open the verifier UI in your browser goint to http://localhost:8003.

Introduce yor URL in the text form and click at Search:
![Beacon verifier v2 UI](https://github.com/EGA-archive/beacon-verifier-v2/blob/main/ui_image.png)
