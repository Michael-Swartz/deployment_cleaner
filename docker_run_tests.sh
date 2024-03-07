#!/bin/bash

TAG="deployment_cleanup:latest"

# Build container
docker build . -t "${TAG}"

# Run pytest
docker run -it -v ~/.aws:/root/.aws "${TAG}" pytest /tests




