<h1 align="center"> 🌊 Seigaiha </h1>

<p align="center">
  <a href="./README.md"><img src="./docs/examples/banner.png" alt="banner" width="100%" /></a>
</p>

<p align="center">
    <a href="https://github.com/ToshY/seigaiha/actions/workflows/pylint.yml/badge.svg"><img src="https://github.com/ToshY/seigaiha/actions/workflows/pylint.yml/badge.svg" alt="Pylint" style="max-width: 100%;"></a>
    <a href="https://github.com/ToshY/seigaiha/actions/workflows/security.yml/badge.svg"><img src="https://github.com/ToshY/seigaiha/actions/workflows/security.yml/badge.svg" alt="Pip Audit" style="max-width: 100%;"></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/Code%20Style-Black-000000.svg" alt="Code Style: Black" data-canonical-src="https://img.shields.io/badge/Code%20Style-Black-000000.svg" style="max-width: 100%;"></a>
</p>

## Introduction

### Background information

_Seigaiha_ (**kanji**: 清海波 ; **hiragana**: せいがいは ; **translation**: "Blue sea and waves" / wave crest pattern) is a pattern originating from China, used for depicting seas on ancient maps.
Excavation in Japan (Gunma) shows its first appearance roughly around the 6th century on the clothing of a funerary clay figure ([_haniwa_](https://www.khanacademy.org/humanities/art-asia/art-japan/kofun-period/a/haniwa-warrior)).
The origin of _Seigaiha_ is believed to be derived from the motif on clothing used at [_Gagaku_ performance](https://www.kunaicho.go.jp/e-culture/gagaku.html) named "Seigaiha". <sup>[1]</sup>

[1]: https://project-japan.jp/seigaiha/

### About 

This tool was written to create custom traditional and modern (polygon) wave patterns through the usage of JSON
presets.

## Setup

### 🐋 Docker

Run from existing image.

```shell
docker run -it \
  --volume $HOME/seigaiha/output:/output \
  --volume $HOME/seigaiha/custom_preset.json:/app/preset/custom_preset.json \
  --name seigaiha t0shy/seigaiha:latest \
  python seigaiha.py -p "custom_preset.json"
```

> Note: JSON presets must be placed in the `/app/preset` directory of the container.

### 🐋 Docker Compose

To simplify development and/or usage, a [`Taskfile.yml`](./Taskfile.yml) is included for usage with Docker Compose.
Installation guide for Task can be found at [taskfile.dev/installation](https://taskfile.dev/installation/).

#### Build

Build local image and up the `seigaiha` service.

```shell
task docker:up
```

#### Use

Create a seigaiha pattern either by file or string.

`File`

```shell
task seigaiha p="default.json"
```

`String`

```shell
task seigaiha p='{"width":2500,"fractions":11,"edges":36,"spacing":0.3,"rotation":0,"pattern":true,"repeat":{"horizontal":{"amount":10,"spacing":1},"vertical":{"amount":20,"spacing":0.25},"broken":{"factor":0,"fractions":4,"colours":[{"R":0,"G":0,"B":0,"A":1},{"R":0,"G":0,"B":0,"A":1},{"R":0,"G":0,"B":0,"A":1},{"R":200,"G":191,"B":231,"A":1}]},"alternate":1},"colours":[{"R":65,"G":124,"B":192,"A":1},{"R":255,"G":255,"B":255,"A":1}]}'
```

#### Remove

Clean local image and down the `seigaiha` service.

```shell
task docker:down
```

## Create a preset

Before a pattern can be created a JSON preset is required. To make things easier, an example is already provided in
the `preset` directory. If you just want to try it out and see the results, you can continue to the next step.

For creating of custom wave patterns, please check out the [following documentation](./docs/PRESET.md) on how to get started.

## 🛠️ Contribute

### Pre-commit

Setting up `pre-commit` code style & quality checks for local development.

```shell
pre-commit install
```

### Quality & Code Style

```shell
task cs:check
```

### Code Style fix

```shell
task cs:fix
```

## ❕ License

This repository comes with [no license](https://choosealicense.com/no-permission/).