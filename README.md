# Deployment Cleaner

Script that will allow you to specify a specific number of deployments to keep in an S3 bucket, and will delete the rest.

### Assumptions

- Directories (deployments) are a short sha commit hash
- We assume the newest directory (based on the last modified date of the oldest object in a deployment) is the latest version of the deployment
- Objects in the bucket are immutable

The structure of the bucket looks like:
```
s3://<bucket>
├── 2wse34dx
│   ├── css
│   │   └── font.css
│   ├── images
│   │   └── hey.png
│   └── root.html
├── 45tgbvfr
│   ├── css
│   │   └── font.css
│   ├── images
│   │   └── hey.png
│   └── root.html
├── cde34drf
│   ├── css
│   │   └── font.css
│   ├── images
│   │   └── hey.png
│   └── root.html
...
```

## Usage

```
$ python3 deployment_cleaner.py --help                                                                       

usage: deployment_cleaner.py [-h] [--dry-run] --deployments DEPLOYMENTS --bucket BUCKET
                             [--endpoint-url ENDPOINT_URL]

options:
  -h, --help            show this help message and exit
  --dry-run             Run script in dry-run mode to see objects that will be deleted without deleting them.
  --deployments DEPLOYMENTS
                        Number of deployments to retain, this will retain the X number of most recent
                        deployments
  --bucket BUCKET       Bucket from which you will delete the objects from
  --endpoint-url ENDPOINT_URL
                        Optional argument for specifying a different s3 endpoint URL. Useful for local testing
                        with localstack
```

A successful run of the utility will look like the following:
```
$ python3 deployment_cleaner.py --deployments 2 --bucket deployments --endpoint-url "http://localhost:4566"                                     
[2024-03-07T08:13:20 -- INFO] Starting deployment cleaner...
[2024-03-07T08:13:20 -- INFO] Deleting deployment: 2wse34dx
[2024-03-07T08:13:20 -- INFO] Deleting deployment: gy76yt5r
[2024-03-07T08:13:20 -- INFO] Deleting deployment: mki87ujh
[2024-03-07T08:13:20 -- INFO] Deleting deployment: 45tgbvfr
[2024-03-07T08:13:20 -- INFO] Finished
```

### Setup

Run the following to install the required libraries:
```
pip install -r requirements.txt
```

## Testing/Development

Inside the `dev/` directory run the following command to bring up a localstack container mocking an S3 bucket:

```
docker-compose up
```

When the container comes up for the first time it will populate the S3 bucket named `deployments` with dummy data for testing. When testing against localstack you should pass `--endpoint-url` the value of your local machines IP address.

### Running inside docker

Included are two scripts to allow you to run the tool, and run the tests within a docker container. You can pass `./deployment_cleaner.sh` the same arguments that you would pass to `deployment_cleaner.py`

### Example running against localstack

```
./deployment_cleaner.sh --dry-run --bucket deployments --deployments 2 --endpoint-url http://<local IP>:4566
```

### Unit Tests

Included are unit tests. To run the unit tests run the followng:
```
./docker_run_tests.sh
```