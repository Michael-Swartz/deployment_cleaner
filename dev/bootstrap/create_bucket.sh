#!/usr/bin/env bash
set -x
awslocal s3 mb s3://deployments

# We sleep here to mock deploying at different times
cd /tmp/dev_data
for dir in $(find . -maxdepth 1 -mindepth 1 -type d);
do
    awslocal s3 cp $dir s3://deployments/$dir --recursive
    sleep 3
done
set +x
