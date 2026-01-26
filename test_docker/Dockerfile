FROM python:3.12-slim

RUN apt update && apt install -y curl vim git

COPY . /opt/sumit

RUN cd /opt/sumit && pip install . --index-url https://pypi.org/simple