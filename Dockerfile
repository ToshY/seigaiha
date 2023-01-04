FROM python:3.10-slim

LABEL maintainer="ToshY (github.com/ToshY)"

ENV PIP_ROOT_USER_ACTION ignore

WORKDIR /app

RUN apt-get update \
    && apt-get install -y libcairo2 libimage-exiftool-perl

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
