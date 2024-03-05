#!/usr/bin/env bash
set -x
awslocal s3 mb s3://deployments
ls
awslocal s3 cp /tmp/dev_data/ s3://deployments/ --recursive
set +x
