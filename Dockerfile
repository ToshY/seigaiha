FROM python:3.10-slim

LABEL maintainer="ToshY (github.com/ToshY)"

ARG UID=${UID:-10000}
ARG GID=${GID:-10001}
ARG USER=${USER:-seigaiha}

USER root

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

RUN apt-get update \
    && apt-get install -y libcairo2

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /output

RUN addgroup \
    --gid $GID \
    --system $USER \
    && adduser \
    --uid $UID \
    --disabled-password \
    --gecos "" \
    --ingroup $USER \
    --no-create-home \
    $USER

RUN chown $UID:$GID /output

CMD ["/bin/bash"]