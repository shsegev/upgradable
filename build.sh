#!/bin/bash

docker build --no-cache -t upservice:${1} .
docker save -o upservice.tar upservice:${1}
# docker rmi upservice:${1}