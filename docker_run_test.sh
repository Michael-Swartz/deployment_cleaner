#!/bin/bash

TAG="deployment_cleanup:latest"

# Build container
docker build . -t "${TAG}"

docker run -it -v ~/.aws:/root/.aws -e AWS_PROFILE=default "${TAG}" pytest /tests




