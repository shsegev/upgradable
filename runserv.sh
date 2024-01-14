#!/bin/bash
docker rm -f upservice || true
docker run --restart always --privileged --network host -d   \
     -v /var/run/docker.sock:/var/run/docker.sock\
     -e UNIT_HOST=${UNIT_HOST} -e UNIT_PASSWORD=${UNIT_PASSWORD} -e UNIT_PORT=${UNIT_PORT}\
     --name upservice upservice:latest