#!/bin/bash

TAG="deployment_cleanup:latest"

# Build container
docker build . -t "${TAG}"

# Run deployment cleaner
docker run -it -v ~/.aws:/root/.aws "${TAG}" python3 /deployment_cleaner.py "$@"




