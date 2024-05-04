#!/bin/bash -e
curl -X POST -H 'Content-Type: application/json' \
    -d '{"username":"admin\ninjection", "password": "admin"}' \
    http://localhost:8000/login