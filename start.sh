#!/bin/bash

docker compose -f docker-compose.prod.yml -p django-celery-prod up -d --build