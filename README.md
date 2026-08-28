<h1 align="center"> 🌊 Seigaiha </h1>

<p align="center">
  <a href="./README.md"><img src="./docs/images/banner.png" alt="banner" width="100%" /></a>
</p>

<div align="center">
        <img src="https://img.shields.io/github/v/release/toshy/seigaiha?label=Release&sort=semver" alt="Current bundle version" />
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/seigaiha/codestyle.yml?branch=main&label=Black" alt="Black">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/seigaiha/codequality.yml?branch=main&label=Ruff" alt="Ruff">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/seigaiha/statictyping.yml?branch=main&label=Mypy" alt="Mypy">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/seigaiha/test.yml?branch=main&label=Pytest" alt="Pytest">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/seigaiha/security.yml?branch=main&label=Security%20check" alt="Security check" />
    <br /><br />
    <div>A command-line utility for creating custom traditional and modern wave patterns.</div>
</div>

## 💭 History

_Seigaiha_ (**kanji**: 清海波 ; **hiragana**: せいがいは ; **translation**: "Blue sea and waves" / wave crest pattern) is a
pattern originating from China, used for depicting seas on ancient maps.

Excavation in Japan (Gunma) shows its first appearance roughly around the 6th century on the clothing of a funerary clay
figure ([_haniwa_](https://www.khanacademy.org/humanities/art-asia/art-japan/kofun-period/a/haniwa-warrior)).

The origin of _Seigaiha_ is believed to be derived from the motif on clothing used at a [_Gagaku_ performance](https://www.kunaicho.go.jp/e-culture/gagaku.html) named "Seigaiha". <sup>[1]</sup>

[1]: https://project-japan.jp/seigaiha/

## 📝 Quickstart

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/seigaiha:latest -h
```

## 📜 Documentation

The documentation is available at [https://toshy.github.io/seigaiha](https://toshy.github.io/seigaiha).

## 🛠️ Contribute

### Requirements

* ☑️ [Pre-commit](https://pre-commit.com/#installation).
* 🐋 [Docker Compose V2](https://docs.docker.com/compose/install/)
* 📋 [Task 3.37+](https://taskfile.dev/installation/)

## ❕ License

This repository comes with a [BSD 3-Clause License](./LICENSE).
