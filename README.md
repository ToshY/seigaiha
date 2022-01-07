# 🌊 Seigaiha

Seigaiha (kanji: 清海波 ; hiragana: せいがいは) is a traditional Japanese pattern of blue waves.

## Introduction
This python command line tool is made to create your own custom traditional or modern wave patterns through simple JSON presets.

## Setup

### 🐋 Docker Compose

```shell
make up
```

### 🐍 Standard
Install the requirements with `pip`
```shell
pip install -r requirements.txt
```

Install the `libcairo2` package

```shell
apt install libcairo2
```

## Create a preset

Before you can use the tool, a JSON preset is needed. To make things easier, an example is already provided in the `preset` directory. If you just want to try it out and see the results, you can continue to the next step.

If you're looking to make your own custom wave patterns, please check out the [the following documentation]() on how to get started.


## Use it!

### 🐋 Docker Compose

```shell
make seigaiha preset="preset/pattern_preset.json" output="output"
```

The volume is mounted as `./output:/app/output`, which can be changed by editing the `docker-compose.yml` file to fit the user preferences.

### 🐍 Standard
```shell
python seigaiha.py -p preset/pattern_preset.json -o output
```