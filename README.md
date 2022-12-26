<h1 align="center"> 🌊 Seigaiha </h1>

<p align="center">
  <a href="./README.md"><img src="./docs/examples/banner.png" alt="banner" width="100%" /></a>
</p>

<div align="center">
    <img src="https://img.shields.io/github/v/release/toshy/seigaiha?label=Release&sort=semver" alt="Current bundle version" />
    <a href="https://hub.docker.com/r/t0shy/seigaiha"><img src="https://img.shields.io/badge/Docker%20Hub-t0shy%2Fseigaiha-blue" alt="Docker Hub" /></a>
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/seigaiha/pylint.yml?branch=main&label=Pylint" alt="Code style">
    <img src="https://img.shields.io/badge/Code%20Style-PEP8-orange.svg" alt="Code style" />
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/seigaiha/security.yml?branch=main&label=Security%20check" alt="Security check" />
    <br /><br />
</div>

## Introduction

### Background information

_Seigaiha_ (**kanji**: 清海波 ; **hiragana**: せいがいは ; **translation**: "Blue sea and waves" / wave crest pattern) is a
pattern originating from China, used for depicting seas on ancient maps.
Excavation in Japan (Gunma) shows its first appearance roughly around the 6th century on the clothing of a funerary clay
figure ([_haniwa_](https://www.khanacademy.org/humanities/art-asia/art-japan/kofun-period/a/haniwa-warrior)).
The origin of _Seigaiha_ is believed to be derived from the motif on clothing used at [
_Gagaku_ performance](https://www.kunaicho.go.jp/e-culture/gagaku.html) named "Seigaiha". <sup>[1]</sup>

[1]: https://project-japan.jp/seigaiha/

### About

This tool was written to create custom traditional and modern (polygon) wave patterns through the usage of JSON
presets.

## Setup

* You can choose to either follow the [Docker](#-docker--compose) or [Python](#-python) route.
* For help, run `main.py -h`.
* Images are always saved in the `./output` directory (relative to the working directory).
    * In the docker container this will be `/app/output`.

### 🐋 Docker / Compose

#### Docker

1. Pull the image `t0shy/seigaiha:latest`.

```shell
docker pull t0shy/seigaiha:latest
```

or build from source.

```shell
docker build -t t0shy/seigaiha:latest --no-cache .
```

2. Run it.

From JSON file

```shell
docker run -it --rm \
  -v ${PWD}/output:/app/output \
  -v ${PWD}/default.json:/app/preset/default.json \
  --name seigaiha t0shy/seigaiha:latest \
  python main.py -p "default.json"
```

From JSON string

```shell
docker run -it --rm \
  -v ${PWD}/output:/app/output \
  -v ${PWD}/default.json:/app/preset/default.json \
  --name seigaiha t0shy/seigaiha:latest \
  python main.py -p '{"width":2500,"fractions":11,"edges":36,"spacing":0.3,"rotation":0,"pattern":true,"repeat":{"horizontal":{"amount":10,"spacing":1},"vertical":{"amount":20,"spacing":0.25},"broken":{"factor":0,"fractions":4,"colours":[{"R":0,"G":0,"B":0,"A":1},{"R":0,"G":0,"B":0,"A":1},{"R":0,"G":0,"B":0,"A":1},{"R":200,"G":191,"B":231,"A":1}]},"alternate":1},"colours":[{"R":65,"G":124,"B":192,"A":1},{"R":255,"G":255,"B":255,"A":1}]}'
```

> Note: JSON presets must be mapped to be inside the `/app/preset` directory of the container.

#### Docker Compose

To simplify development and/or usage, a [`Taskfile.yml`](./Taskfile.yml) is included for usage with Docker Compose.
Installation guide for Task can be found at [taskfile.dev/installation](https://taskfile.dev/installation/).

1. Create a `docker-compose.yml`.

```yaml
version: '3.9'

services:
  seigaiha:
    image: t0shy/seigaiha:latest
    volumes:
      - ./output/:/app/output
      - ./default.json:/app/preset/default.json
````

2. Up the service.

```shell
docker compose up -d --remove-orphans
```

3. Run it.

From JSON file

```shell
docker compose run --rm seigaiha python main.py -p "default.json"
```

From JSON string

```shell
docker compose run --rm seigaiha python main.py -p '{"width":2500,"fractions":11,"edges":36,"spacing":0.3,"rotation":0,"pattern":true,"repeat":{"horizontal":{"amount":10,"spacing":1},"vertical":{"amount":20,"spacing":0.25},"broken":{"factor":0,"fractions":4,"colours":[{"R":0,"G":0,"B":0,"A":1},{"R":0,"G":0,"B":0,"A":1},{"R":0,"G":0,"B":0,"A":1},{"R":200,"G":191,"B":231,"A":1}]},"alternate":1},"colours":[{"R":65,"G":124,"B":192,"A":1},{"R":255,"G":255,"B":255,"A":1}]}'
```

## Create a preset

Before an image can be created, a JSON preset is required. To make things easier, an example is already provided in
the preset directory: [`./preset/default.json`](./preset/default.json). If you just want to try it out and see the
results, you can continue to the next step.

For creating of custom wave patterns, please check out the [following documentation](./docs/PRESET.md) on how to get
started.

## 🛠️ Contribute

### Prerequisites

* Docker Compose
    * See the Docker Compose [installation guide](https://docs.docker.com/compose/install/) to get started.
* Task
    * See the Task [installation guide](https://taskfile.dev/installation/) to get started

### Pre-commit

Setting up `pre-commit` code style & quality checks for local development.

```shell
pre-commit install
```

### Checks

```shell
task contribute
```

> Note: you can use `task tools:black:fix` to resolve codestyle issues.

## ❕ License

This repository comes with [no license](https://choosealicense.com/no-permission/).