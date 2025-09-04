FROM python:3.13-slim

RUN apt update && apt install -y curl vim

COPY . /opt/sumit

RUN cd /opt/sumit && pip install .