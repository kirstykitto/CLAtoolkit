#!/bin/bash

docker rm -f $(docker ps -a -q)

docker-compose build
docker-compose up -d
