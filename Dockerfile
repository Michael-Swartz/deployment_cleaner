FROM python:3.10

RUN pip install boto3 semver pytest

COPY ./deployment_cleanup.py /
COPY ./tests /tests/