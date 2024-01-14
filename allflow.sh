#!/bin/bash
docker rm -f upservice || true
docker rm -f upservice_old || true
docker images -q --filter "reference=upservice*" | xargs docker rmi -f

docker build --no-cache -t upservice:1.10 .
docker tag upservice:1.10 upservice:latest
docker run --restart always --privileged --network host -d   \
     -v /var/run/docker.sock:/var/run/docker.sock\
     -e UNIT_HOST=${UNIT_HOST} -e UNIT_PASSWORD=${UNIT_PASSWORD} -e UNIT_PORT=${UNIT_PORT}\
     --name upservice upservice:latest
docker build --no-cache -t upservice:1.11 .
docker save -o upservice.tar upservice:1.11
docker rmi upservice:1.11
docker logs -f upservice &
curl -X 'POST' \
  'http://127.0.0.1:8000/upload_new' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@upservice.tar;type=application/x-tar'