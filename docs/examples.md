# Examples

## Usage

Add your files to the input directory of the mounted container.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/seigaiha:latest
```

* By default, it will find all files from the `/app/input` directory (recursively) and write the output to the `/app/output` directory. 
* Depending on the input options, either only a single polygon and/or a pattern will be created.

<div markdown="span" style="display: flex; justify-content: space-between;">
    <figure style="width: 100%; text-align: center;">
        ![banner_single.png](./images/banner_single.png){ width="25%" height=50% }
        <figcaption style="margin-top: 5px;"><code>output/banner.png</code></figcaption>
    </figure>
    <figure style="width: 100%; text-align: center;">
        ![banner.png](./images/banner.png){ width="100%" height=auto }
        <figcaption style="margin-top: 5px;"><code>output/banner_seigaiha.png</code></figcaption>
    </figure>
</div>

!!! question

    The image generated above uses the [`banner`](#banner) preset.

!!! note

    - By default, if no explicit `-e/--extension` argument is provided, both SVG and PNG output files will be created.
    - By default, output file names contain datetime in format `%d-%m-%Y_%H-%M-%S-%f`. You can disable this behavior by
      passing the `--no-unique-filename` argument.

### Specific file

Convert only a specific file and writing output to `/app/output` (default).

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input/custom.json:/app/input/custom.json \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/seigaiha:latest \
  -i "input/custom.json" 
```

### Specific file with PNG extension only

Convert only a specific file and write the PNG output to `/app/output`.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input/custom.json:/app/input/custom.json \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/seigaiha:latest \
  -i "input/custom.json" \
  -e '["png"]'
```

!!! note

    The `-e/--extension` argument requires one of the following values: 

    - `'["svg", "png"]'` (default)
    - `'["svg"]'`
    - `'["png"]'`


### Single file with output subdirectory

Convert only a specific file and writing output to `/app/output/dir1`.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input/custom.json:/app/input/custom.json \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/seigaiha:latest \
  -i "input/custom.json" \
  -o "output/result"
```

### Specific subdirectory

Convert files in specific subdirectory and writing output to `/app/output/dir1`.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/seigaiha:latest \
  -i "input/dir1" \
  -o "output/dir1"
```

### Multiple inputs

Convert files in multiple input subdirectories and writing output to `/app/output` (default).

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/seigaiha:latest \
  -i "input/dir1" \
  -i "input/dir2"
```

### Multiple inputs and outputs

Convert files in multiple input subdirectories and writing output to specific output subdirectories respectively.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/seigaiha:latest \
  -i "input/dir1" \
  -i "input/dir2" \
  -o "output/dir1" \
  -o "output/dir2"
```

## Presets

### Banner

???+ example "`input/banner.json`"

    Create blue-white Seigaiha modern polygon pattern. 

    ```json
    {
        "fractions": 11,
        "edges": 7,
        "spacing": 0.3,
        "rotation": 0,
        "pattern": {
            "horizontal": {
                "amount": 10,
                "spacing": 1
            },
            "vertical": {
                "amount": 20,
                "spacing": 0.25
            },
            "broken": {
                "factor": 0,
                "factor_rounding": "round",
                "fractions": 4,
                "skip_edge": true,
                "colours": [
                    {
                        "R": 0,
                        "G": 0,
                        "B": 0,
                        "A": 1
                    },
                    {
                        "R": 0,
                        "G": 0,
                        "B": 0,
                        "A": 1
                    },
                    {
                        "R": 0,
                        "G": 0,
                        "B": 0,
                        "A": 1
                    },
                    {
                        "R": 200,
                        "G": 191,
                        "B": 231,
                        "A": 1
                    }
                ],
                "images": []
            },
            "alternate": 1
        },
        "colours": [
            {
                "R": 65,
                "G": 124,
                "B": 192,
                "A": 1
            },
            {
                "R": 255,
                "G": 255,
                "B": 255,
                "A": 1
            }
        ],
        "output": {
            "resolution": 2500,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {
                    "shape-rendering": "crispEdges",
                    "transform-origin": "top left"
                }
            }
        }
    }
    ```

    <div markdown="span" style="display: flex; justify-content: space-between;">
        <figure style="width: 100%; text-align: center;">
            ![banner.png](./images/banner.png){ width="75%" height=auto }
            <figcaption style="margin-top: 5px;"><code>output/banner_seigaiha.png</code></figcaption>
        </figure>
    </div>

### Repeatable pattern

???+ example "`input/basic.json`"

    The simplest repeatable patterns can be created by using the following pattern options:
    ```json
    "pattern": {
        "horizontal": {
            "amount": 3,
            "spacing": 1
        },
        "vertical": {
            "amount": 6,
            "spacing": 0.25
        },
        "alternate": 1
    }
    ```

    A complete preset example would like this:
    ```json
    {
        "fractions": 10,
        "edges": 36,
        "spacing": 0.3,
        "rotation": 0,
        "pattern": {
            "horizontal": {
                "amount": 3,
                "spacing": 1
            },
            "vertical": {
                "amount": 6,
                "spacing": 0.25
            },
            "alternate": 1
        },
        "colours": [
            {
                "R": 65,
                "G": 124,
                "B": 192,
                "A": 1
            },
            {
                "R": 255,
                "G": 255,
                "B": 255,
                "A": 1
            }
        ],
        "output": {
            "resolution": 2500,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {
                    "shape-rendering": "crispEdges",
                    "transform-origin": "top left"
                }
            }
        }
    }
    ```

    <div markdown="span" style="display: flex; justify-content: space-between;">
        <figure style="width: 100%; text-align: center;">
            ![basic_pattern_plain.png](./images/basic_pattern_plain.png){ width="75%" height=auto }
            <figcaption style="margin-top: 5px;"><code>output/basic_seigaiha.png</code></figcaption>
        </figure>
    </div>

### Polygon edges

The `edges` option can be used to create polygon edges. It denotes the number of sides each polygon has.

???+ example "`input/4_edges.json`"

    This example shows a pattern where each polygon has 4 edges (squares) and is rotated by 90 degrees. Also, the `amount` options for the `horizontal` and `vertical` patterns are set to 10 and 25 respectively, creating a larger pattern.

    ```json
    {
        "fractions": 5,
        "edges": 4,
        "spacing": 0,
        "rotation": 90,
        "pattern": {
            "horizontal": {
                "amount": 10,
                "spacing": 1
            },
            "vertical": {
                "amount": 20,
                "spacing": 0.25
            },
            "alternate": 1
        },
        "colours": [
            {
                "R": 0,
                "G": 0,
                "B": 0,
                "A": 1
            },
            {
                "R": 2,
                "G": 94,
                "B": 133,
                "A": 1
            },
            {
                "R": 4,
                "G": 168,
                "B": 236,
                "A": 1
            },
            {
                "R": 154,
                "G": 207,
                "B": 244,
                "A": 1
            },
            {
                "R": 200,
                "G": 191,
                "B": 231,
                "A": 1
            }
        ],
        "output": {
            "resolution": 2500,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {
                    "shape-rendering": "crispEdges",
                    "transform-origin": "top left"
                }
            }
        }
    }
    ```

    <div markdown="span" style="display: flex; justify-content: space-between;">
        <figure style="width: 100%; text-align: center;">
            ![4_edges_rotate_pattern.png](./images/4_edges_rotate_pattern.png){ width="75%" height=auto }
            <figcaption style="margin-top: 5px;"><code>output/4_edges_rotate_seigaiha.png</code></figcaption>
        </figure>
    </div>

???+ example "`input/7_edges.json`"

    This example shows a pattern where each polygon has 7 edges. Also, the `amount` options for the `horizontal` and `vertical` patterns are set to 20 and 50 respectively, creating a larger pattern.

    ```json
    {
        "fractions": 9,
        "edges": 7,
        "spacing": 0.25,
        "rotation": 0,
        "pattern": {
            "horizontal": {
                "amount": 20,
                "spacing": 1
            },
            "vertical": {
                "amount": 50,
                "spacing": 0.25
            },
            "broken": {
                "factor": 0.15,
                "factor_rounding": "floor",
                "fractions": 2,
                "colours": [
                    {
                        "R": 0,
                        "G": 0,
                        "B": 0,
                        "A": 1
                    },
                    {
                        "R": 150,
                        "G": 123,
                        "B": 0,
                        "A": 1
                    }
                ]
            },
            "alternate": 1
        },
        "colours": [
            {
                "R": 0,
                "G": 0,
                "B": 0,
                "A": 1
            },
            {
                "R": 150,
                "G": 123,
                "B": 0,
                "A": 1
            }
        ],
        "output": {
            "resolution": 2500,
            "mega_pixel_constraint": null,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {
                    "shape-rendering": "crispEdges",
                    "transform-origin": "top left"
                }
            }
        }
    }
    ```

    <div markdown="span" style="display: flex; justify-content: space-between;">
        <figure style="width: 100%; text-align: center;">
            ![7_edges_pattern_large.png](./images/7_edges_pattern_large.png){ width="75%" height=auto }
            <figcaption style="margin-top: 5px;"><code>output/7_edges_seigaiha.png</code></figcaption>
        </figure>
    </div>

### Yabure Seigaiha

The "Yabure" Seigaiha pattern is a more complex pattern that uses the `broken` option to create a "broken" Seigaiha pattern.

???+ example "`input/yabure_seigaiha.json`"

    ```json
    {
        "fractions": 11,
        "edges": 36,
        "spacing": 0.3,
        "rotation": 0,
        "pattern": {
            "horizontal": {
                "amount": 10,
                "spacing": 1
            },
            "vertical": {
                "amount": 20,
                "spacing": 0.25
            },
            "broken": {
                "factor": 0.2, 
                "factor_rounding": "ceil",
                "fractions": 2,
                "skip_edge": true,
                "colours": [
                    {
                        "R": 0,
                        "G": 0,
                        "B": 0,
                        "A": 1
                    },
                    {
                        "R": 255,
                        "G": 215,
                        "B": 0,
                        "A": 1
                    }
                ],
                "images": []
            },
            "alternate": 1
        },
        "colours": [
            {
                "R": 0,
                "G": 0,
                "B": 0,
                "A": 1
            },
            {
                "R": 255,
                "G": 215,
                "B": 0,
                "A": 1
            }
        ],
        "output": {
            "resolution": 2500,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {
                    "shape-rendering": "crispEdges",
                    "transform-origin": "top left"
                }
            }
        }
    }
    ```

    <div markdown="span" style="display: flex; justify-content: space-between;">
        <figure style="width: 100%; text-align: center;">
            ![banner.png](./images/yabure_seigaiha_plain.png){ width="75%" height=auto }
            <figcaption style="margin-top: 5px;"><code>output/yabure_seigaiha_plain_seigaiha.png</code></figcaption>
        </figure>
    </div>

???+ example "`input/3_edges_rotate_yabure.json`"

    ```json
    {
        "fractions": 5,
        "edges": 3,
        "spacing": 0.3,
        "rotation": 30,
        "pattern": {
            "horizontal": {
                "amount": 10,
                "spacing": 1
            },
            "vertical": {
                "amount": 20,
                "spacing": 0.25
            },
            "broken": {
                "factor": 0.15,
                "factor_rounding": "round",
                "fractions": 5,
                "colours": [
                    {
                        "R": 0,
                        "G": 0,
                        "B": 0,
                        "A": 1
                    },
                    {
                        "R": 200,
                        "G": 191,
                        "B": 231,
                        "A": 1
                    }
                ]
            },
            "alternate": 1
        },
        "colours": [
            {
                "R": 0,
                "G": 0,
                "B": 0,
                "A": 1
            },
            {
                "R": 85,
                "G": 0,
                "B": 170,
                "A": 1
            }
        ],
        "output": {
            "resolution": 2500,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {
                    "shape-rendering": "crispEdges",
                    "transform-origin": "top left"
                }
            }
        }
    }
    ```

    <div markdown="span" style="display: flex; justify-content: space-between;">
        <figure style="width: 100%; text-align: center;">
            ![3_edges_rotate_yabure_pattern.png](./images/3_edges_rotate_yabure_pattern.png){ width="75%" height=auto }
            <figcaption style="margin-top: 5px;"><code>output/3_edges_rotate_yabure_seigaiha.png</code></figcaption>
        </figure>
    </div>

???+ example "`input/7_edges_yabure.json`"

    Similar to preset `input/7_edges.json` but with broken polygons.

    ```json
    {
        "fractions": 9,
        "edges": 7,
        "spacing": 0.25,
        "rotation": 0,
        "pattern": {
            "horizontal": {
                "amount": 20,
                "spacing": 1
            },
            "vertical": {
                "amount": 50,
                "spacing": 0.25
            },
            "broken": {
                "factor": 0.15,
                "factor_rounding": "floor",
                "fractions": 2,
                "colours": [
                    {
                        "R": 0,
                        "G": 0,
                        "B": 0,
                        "A": 1
                    },
                    {
                        "R": 150,
                        "G": 123,
                        "B": 0,
                        "A": 1
                    }
                ]
            },
            "alternate": 1
        },
        "colours": [
            {
                "R": 0,
                "G": 0,
                "B": 0,
                "A": 1
            },
            {
                "R": 150,
                "G": 123,
                "B": 0,
                "A": 1
            }
        ],
        "output": {
            "resolution": 2500,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {
                    "shape-rendering": "crispEdges",
                    "transform-origin": "top left"
                }
            }
        }
    }
    ```

    <div markdown="span" style="display: flex; justify-content: space-between;">
        <figure style="width: 100%; text-align: center;">
            ![7_edges_yabure_seigaiha_pattern_large.png](./images/7_edges_yabure_seigaiha_pattern_large.png){ width="75%" height=auto }
            <figcaption style="margin-top: 5px;"><code>output/7_edges_yabure_seigaiha.png</code></figcaption>
        </figure>
    </div>


???+ example "`input/yabure_image.json`"

    It is also possible to fill in the broken parts of the pattern with an image, for which you can use the `images` option (under `broken`) to do so. This option requires atleast one base64 encoded SVG image.

    ```json
    {
        "fractions": 11,
        "edges": 36,
        "spacing": 0.3,
        "rotation": 0,
        "pattern": {
            "horizontal": {
                "amount": 10,
                "spacing": 1
            },
            "vertical": {
                "amount": 20,
                "spacing": 0.25
            },
            "broken": {
                "factor": 0.2, 
                "factor_rounding": "ceil",
                "fractions": 2,
                "skip_edge": true,
                "colours": [
                    {
                        "R": 0,
                        "G": 0,
                        "B": 0,
                        "A": 1
                    },
                    {
                        "R": 255,
                        "G": 215,
                        "B": 0,
                        "A": 1
                    }
                ],
                "images": [
                    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIiBbCgk8IUVOVElUWSBuc19zdmcgImh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KCTwhRU5USVRZIG5zX3hsaW5rICJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIj4KXT4KPHN2ZyB4bWxuczpzdmc9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZlcnNpb249IjEuMSIgd2lkdGg9Ijg0Mi4yMzA4MyIgaGVpZ2h0PSI4MzIuMTQ4MzgiIHZpZXdCb3g9IjAgMCA4NDIuMjMwODMgODMyLjE0ODM4Ij48cGF0aCBzdHlsZT0iZmlsbDojMDAwMDAwIiBkPSJtIDMyMi41NzM3Miw4MzEuMTY5NTEgYyAtMTAuMjQ3NywtMS43MDU1IC0zNS45NDUxMywtOS43ODIgLTU1LjQ5OTA0LC0xNy40NDI5IC03MC44NTY2NywtMjcuNzYwNjggLTEzNS4zOTI3NiwtNzYuNjc4NzUgLTE4MS41Mzc0MzMsLTEzNy42MDQ2IC0yNC40MzExNywtMzIuMjU3IC0zMC4wMzY0LC00NC4xMzE4IC0zMS4wMDYwNSwtNjUuNjg2NiAtMC4zODA5MiwtOC40Njc3IC0wLjEyMDcyLC0xMy4yMjcyIDEuMDM0OTQsLTE4LjkzMDU4IDQuNjMwNzMsLTIyLjg1MzU2IDE4LjUzMjY4LC00Mi4wMzMxNiAzOS4wNDU4OCwtNTMuODY4OTcgNS4xNTQwNSwtMi45NzM4MiA2Mi4xNTU1ODMsLTIxLjU5MTUxIDYxLjQ4MjA0MywtMjAuMDgxMTEgLTguMTM1NDIsMTguMjQzODEgLTguMTUzOTEsMjguNjk0MTUgLTAuMDc5MSw0NC43Mjg1NCA0Ljc2NjkzLDkuNDY1ODUgMTQuMzE2NDcsMjQuODU1OTcgMjEuNjczNTQsMzQuOTI5MjIgNDAuMjE5NDMsNTUuMDY4NCA5NS4xOTQ4Nyw5My44OTMzIDE1OS42OTg3LDExMi43ODMxIDEyLjYzMTU1LDMuNjk5MSAzNi43NTE3OSw4Ljc4MjY1IDQxLjY3MTg2LDguNzgyNjUgMTAuMTA0NTIsMCAyMy4wNDE0MywtNS40Mzc1NSAzMC44MDksLTEyLjk0OTM1IGwgMy41NzQ2MSwtMy40NTY5IC0wLjMzNDYsMzMuMjgxMjUgYyAtMC4zMjAwMSwzMS44MzE3NyAtMC40MjkzNywzMy41NjcwNyAtMi41MTEwMSwzOS44NDM3NyAtNC44MjIyNywxNC41NDA0IC0xMS40ODk3NCwyNS4wNTA1OCAtMjIuNDMwMTQsMzUuMzU3MzggLTE3LjQ2Njg1LDE2LjQ1NTIgLTQyLjM5NTA0LDI0LjE3NTggLTY1LjU5MzE4LDIwLjMxNTEgeiBtIDE3MS44NDQ3MSwtMC4yOTY5IGMgLTI1LjY4OTg5LC01LjExMzMgLTQ1LjU2NzU5LC0yMC4yNTI3IC01Ni43MDUwNiwtNDMuMTg4MDggLTcuMDU2ODMsLTE0LjUzMjIgLTcuNTEzNjksLTE3LjgxODEgLTcuNTEzNjksLTU0LjA0MDE3IGwgMCwtMzEuMTcwMDUgMy4wNDY4NywzLjMxMzIgYyA2LjIyMTk3LDYuNzY1OCAxNi41MTYwMiwxMS41MDgwNSAyNy40MDE2NCwxMi42MjMzNSA0LjI3MDU4LDAuNDM3NSA4LjY1Mjc1LDAuMDQ4IDE2LjA3MDk0LC0xLjQyNyA1Ny4xMjAzLC0xMS4zNjA0NSAxMDQuNTIyNTUsLTM0Ljg5MjQ1IDE0Ni43ODk5OSwtNzIuODcxMzUgMTguNDMyOCwtMTYuNTYyNiAzMy42Njk5NywtMzQuMzY0NyA0OC4wMzAyOSwtNTYuMTE1NTEgOS41ODIyLC0xNC41MTM2NyAxNi4yOTM4MiwtMjYuMDYwOTMgMTguNjMxNjMsLTMyLjA1NTUgNC4xNDY1OCwtMTAuNjMyNTkgMy42NzkzLC0yMy4zNjUxNCAtMS4yNDQyNCwtMzMuOTAzMDkgLTIuMDU0OTcsLTQuMzk4MyAtMi40MDQ5OSwtNS44MTMxNyAtMS4zMzY3MSwtNS40MDMyMyAwLjc5NTk5LDAuMzA1NDUgMTMuMzQ1NSw0LjQxNjU3IDI3Ljg4NzgsOS4xMzU4IDE0LjU0MjMsNC43MTkyNCAyOC43NjM2Niw5Ljc0MTY3IDMxLjYwMzAyLDExLjE2MDk0IDEzLjk1MTA4LDYuOTczNTIgMjYuNDc0NTQsMjAuMDEwODQgMzMuNzQzMDMsMzUuMTI3NTggNi4yNzIsMTMuMDQ0MjkgNy45ODg0OCwyMC42OTQxOCA3Ljg4ODM3LDM1LjE1NjIxIC0wLjEzLDE4Ljc3NyAtNC4wNTM2MSwzMC4xNjU1IC0xNi44MjY3Myw0OC44NDAyIC00OC4wMjA4NCw3MC4yMDgyNSAtMTEwLjg5MDY1LDEyMi4wMDYyMiAtMTg3LjA4NjgzLDE1NC4xMzk2IC0xMy44Mzc5Nyw1LjgzNTcgLTQwLjQxMjA5LDE1LjAwNjIgLTU0LjI4NjU3LDE4LjczMzcgLTExLjE4MzY1LDMuMDA0NyAtMjYuNTkzMjYsMy44MzQzIC0zNi4wOTM3NSwxLjk0MzQgeiBtIC0xMTUuMzEyNSwtMTMxLjUyMDYgYyAtNi41NjE1NiwtMC45MjI0IC0yOS42NzgxNCwtNi4xMDMzIC0zNy4wMzEyNSwtOC4yOTk0IC01Ny4xMTI3MSwtMTcuMDU4MSAtMTA3Ljg0MTg5LC01MS44NzE2IC0xNDMuNjczMTIsLTk4LjU5NzMzIC05Ljk3MDAyLC0xMy4wMDE0MiAtMjMuNTI3MDMsLTM0Ljk3OTQ2IC0yOS42NDA1NiwtNDguMDUyMDMgLTIuNzY1NDcsLTUuOTEzMzggLTMuMjkxMDcsLTguMDc0NTggLTMuMzA2LC0xMy41OTM3NSAtMC4wMzA2LC0xMS4zMDEyOSA1Ljc1Mzk2LC0yMC42MTYyNCAxNi4wMTY2MiwtMjUuNzkxOTEgNi4yOTQxMiwtMy4xNzQyNSAxNy41ODIxNywtMy4yODI4MiAyMy43NzkzNSwtMC4yMjg3MSAxOC4zNDMzNyw5LjA0MDA1IDE4LjczOTM5LDMxLjg0NDc0IDAuNjg3ODUsMzkuNjEwMzEgLTUuNTQyMjEsMi4zODQyIC0xMS4xNzEwNiwyLjE5NTQ3IC0xNi45NjgwOCwtMC41Njg5NCAtMS44ODkyNiwtMC45MDA5MiAtMy43NDk2MywtMS4zMjM0NCAtNC4xMzQxNSwtMC45Mzg5MiAtMS4zOTgxNiwxLjM5ODE1IDExLjQ4NzI2LDIyLjg2MDIgMjMuMTQwNiwzOC41NDMxNyAzNS43MTI2OSw0OC4wNjE4MSA4OC44MzM1Niw4My41NDE4MSAxNDcuNDQ3NzYsOTguNDgxODEgNy4xMzczMywxLjgxOTIgMjIuNTM3MDksNS4xMTA4IDIzLjkxNTM1LDUuMTExOCAxLjEyMDAyLDdlLTQgLTAuMjUwODUsLTIuOTM0NCAtMi4yMjIzNiwtNC43NTgzIC01LjYzNzQ3LC01LjIxNTQgLTcuNTU0MzQsLTE1LjY3MSAtNC4xOTc5NCwtMjIuODk3OCAzLjcyOTg2LC04LjAzMSAxMC4xMzU1NiwtMTIuMTcyMiAxOC44NDIxOCwtMTIuMTgxMiA5Ljk1NzQ4LC0wLjAxIDE3LjcwOTc1LDUuMzI5NiAyMi4zNTY5NSwxNS40IDYuMjkyMjEsMTMuNjM1MSAwLjQ5MTE4LDI5Ljc0NDMgLTEzLjE2OTI1LDM2LjU3MDUgLTQuOTIxNjcsMi40NTk0IC02LjY4MjAzLDIuODQ3IC0xMi4zODQzMSwyLjcyNjUgLTMuNjU1OTMsLTAuMDc3IC03LjkxMjc2LC0wLjMxODQgLTkuNDU5NjQsLTAuNTM1OCB6IG0gNjYuODEwMDQsLTAuMTkzNiBjIC03LjU3MDc3LC0yLjQ2NzQgLTE1LjQ1Nzc0LC0xMC4zNzEyIC0xNy45MDI0MywtMTcuOTQwOCAtNS4yOTc0NywtMTYuNDAyNiA0Ljk1NjE0LC0zNC4zMTUzIDIwLjcxMTAzLC0zNi4xODEyIDE4LjQxNTQ0LC0yLjE4MSAyOS45MDU0NiwxOC45MDA4IDE4LjQ2Nzg5LDMzLjg4NDggLTUuMzAxNTEsNi45NDU0IC01Ljc4MzM3LDYuODUyIDEzLjYzMjIyLDIuNjQxNCA2NS4wMDMzNCwtMTQuMDk3MiAxMjUuMDg2OTEsLTU1LjUzMDYgMTYyLjg3MTMsLTExMi4zMTU2MSA1LjczMzUxLC04LjYxNjcgMTUuMjUzNywtMjQuODg0MDIgMTUuMjUzNywtMjYuMDY0MjQgMCwtMS4wNzg0OSAtMi40MjYzOCwtMC43NDM2NCAtNS4yNTg1NCwwLjcyNTcxIC02Ljc2NDM5LDMuNTA5NDEgLTE0Ljk2ODcyLDIuNjE2NDcgLTIxLjg2NTg4LC0yLjM3OTc5IC03Ljc4MzA0LC01LjYzODAxIC0xMC4zNTA5MywtMTcuOTk5OTQgLTUuNDY0OCwtMjYuMzA3NyA1LjA5NjQ2LC04LjY2NTM1IDEyLjI5MTQzLC0xMi41MzA0NCAyMy4yMTQyMiwtMTIuNDcwNTUgOC4yNDY2MiwwLjA0NTIgMTMuNjU3MTQsMi4wOTc1MyAxOS41MzkxMSw3LjQxMTUzIDUuODA1NjEsNS4yNDUwMyA4LjU4NTg5LDExLjkyMDc0IDguNTg1ODksMjAuNjE1NTQgMCw2LjkwNjc0IC0wLjE3NDA2LDcuNDUxMzIgLTUuOTM2NjMsMTguNTczNjggLTEzLjc0ODYzLDI2LjUzNjI0IC0yNy42NjgxNSw0Ni4wMTQ2MyAtNDcuOTY5NjIsNjcuMTI2NjMgLTMzLjk1OTYzLDM1LjMxNTUgLTc3LjE1NTE3LDYxLjM4MTggLTEyNC4yMTg3NSw3NC45NTk3IC0yMi41NTcyOCw2LjUwNzkgLTQ2LjcxNTAzLDkuOTgzOSAtNTMuNjU4NzEsNy43MjA5IHogbSAtMTUyLjI2NTE1LC03Mi42NDg3IGMgLTE1LjgyMTY0LC0zLjgzNzggLTI4LjYxMjMxLC0xNi4yOTcxIC0zMi43OTk4NywtMzEuOTUwMiAtMi4zNjk3MiwtOC44NTgwMiAtMS4xOTgzNiwtMjMuNjA3MzkgMi40MTAzNSwtMzAuMzUwMzMgMS4wNDQ4MywtMS45NTIyOCAwLjY2MTc3LC0yLjY4NDM3IC00LjM5MjI5LC04LjM5NDI1IC0xMC41MzAzOSwtMTEuODk2ODQgLTE0LjI5NDMzLC0yMC45NDM2MyAtMTQuMjk0MzMsLTM0LjM1NzA0IDAsLTE0LjU0MTY4IDQuMDc4NTYsLTI0LjU0MjYzIDEzLjk2NDUxLC0zNC4yNDIxNCBsIDYuMjEwODksLTYuMDkzNzUgNTQuNjgwMDQsLTE3LjY1NDE1IGMgMzAuMDc0MDEsLTkuNzA5NzggNTQuNzU3NzYsLTE3LjUxNDQ3IDU0Ljg1Mjc3LC0xNy4zNDM3NSAwLjA5NSwwLjE3MDcyIDEuNzgwOTksMi43MTE4MiAzLjc0NjY0LDUuNjQ2ODggMi4zNjk3NywzLjUzODQ5IDMuMzExMTEsNS43NzI1OSAyLjc5MzkxLDYuNjMwODIgLTAuNDI5MDEsMC43MTE4OCAtNy45NTE4OSwxMS4xNzc2NSAtMTYuNzE3NTEsMjMuMjU3MjcgLTE1LjI4NDAyLDIxLjA2MjM5IC0xNS45Mzc1LDIyLjE0NDc4IC0xNS45Mzc1LDI2LjM5ODAzIDAsMy43NTkwNCAwLjQ2NzE4LDQuOTAyMjggMy4wNjQ5LDcuNSAyLjUwNTU3LDIuNTA1NTYgMy43OTYyOCwzLjA2NDkgNy4wNzI0OCwzLjA2NDkgMi4yMDQxNywwIDUuMTAyNTUsLTAuNzE3NDUgNi40NDA4NSwtMS41OTQzNCAxLjc3MTgsLTEuMTYwOTQgMjMuMjQ4MDcsLTI5LjY4NDg1IDM0Ljk3MzA1LC00Ni40NDk4IDAuMDg5MSwtMC4xMjc0IDIuMDI2NTIsMC4zNjQ3NyA0LjMwNTM2LDEuMDkzNzIgMi4yNzg4NSwwLjcyODk1IDUuMzEyOCwxLjU4MTg0IDYuNzQyMTIsMS44OTUzMSBsIDIuNTk4NzYsMC41Njk5NCAtMC4yNTUwMSw1OC4zMzYzNCAtMC4yNTUwMSw1OC4zMzYzMyAtMi42OTgwMiw1LjUwMDExIGMgLTEuNDgzOTEsMy4wMjUxIC01LjM3NzUxLDguMzQwNiAtOC42NTI0NCwxMS44MTIyIC05LjQ3OTQyLDEwLjA0ODcgLTIwLjk0OTAxLDE1LjAzNyAtMzQuNTQ5NjMsMTUuMDI2MiAtNy42NjI2OCwtMC4wMSAtMTEuMDgzNjMsLTAuODIzIC0yMi4zMDY0NCwtNS4zMjcgbCAtOC4yMDY1NCwtMy4yOTM1IC0zLjMxMjQ1LDIuOTA4NCBjIC05Ljg2OTg0LDguNjY1OCAtMjUuOTM3MjUsMTIuMzU4NyAtMzkuNDc5NTksOS4wNzM4IHogbSAyMzQuNTE3NjEsLTAuMDMzIGMgLTYuOTEwNTYsLTEuNzc1MiAtMTEuNTk3MTQsLTQuMDAwMyAtMTcuMDc2NDMsLTguMTA3NiBsIC00Ljg4ODkyLC0zLjY2NDcgLTkuNjQyMzMsMy45ODQ1IGMgLTkuNTI3NiwzLjkzNzIgLTkuNzc2MTcsMy45ODQ0IC0yMC44OTIzMiwzLjk2NjMgLTExLjI0NzM1LC0wLjAxOCAtMTEuMjUxOTQsLTAuMDE5IC0xOS40Nzk4MywtMy45MzA4IC0xMC42MTE5LC01LjA0NDkgLTE4LjA1MTg5LC0xMi4yMzgxIC0yMi43MDg5NSwtMjEuOTU1OCBsIC0zLjI3OTk3LC02Ljg0NDEyIDAsLTU3Ljg1MDU0IDAsLTU3Ljg1MDU1IDUuMTIxNDksLTEuNDg4ODYgYyAyLjgxNjgxLC0wLjgxODg3IDUuNzIyMTgsLTEuNzE5MzcgNi40NTYzOCwtMi4wMDExMSAwLjkxODI5LC0wLjM1MjM3IDYuNTYxNCw2LjY2OTU2IDE4LjA4MTY0LDIyLjQ5OTY5IDEyLjQyNDI2LDE3LjA3MjM0IDE3LjU1NjY5LDIzLjQwMTY0IDE5Ljg4NDc2LDI0LjUyMTgxIDYuMDUxOTIsMi45MTE5NSAxMy4zNjU2OSwtMC41MDA4MSAxNS4xMzIxNywtNy4wNjA5OCAxLjI2ODQ2LC00LjcxMDc0IDAuMzkwMTEsLTYuOTA3MzEgLTYuNTUwNzMsLTE2LjM4MTkxIC0zLjA0ODIzLC00LjE2MDk5IC0xMC4zODkyNiwtMTQuMjY1ODIgLTE2LjMxMzQxLC0yMi40NTUxNyBsIC0xMC43NzExNiwtMTQuODg5NzMgMi45OTUwNSwtMy45OTQyNCBjIDEuNjQ3MjgsLTIuMTk2ODMgMy40MjMxNiwtNC43MTQ2OCAzLjk0NjQsLTUuNTk1MjIgMC44NTk4NiwtMS40NDcwNiA2LjEzMDM2LDAuMDc3MiA1NC44MTc3MSwxNS44NTM5NyAzNi4yMTA3OSwxMS43MzM4MSA1NS4wNzk3NSwxOC4yOTQ0NSA1Ny41NjgzMiwyMC4wMTYyMSAyLjAzNjA2LDEuNDA4NjggNS4zNTA5OCw0LjY0NTY0IDcuMzY2NTEsNy4xOTMyNSAxNS4xODg1NCwxOS4xOTgyMiAxNC43MDI1Nyw0My4yODAzMyAtMS4yNTkxOSw2Mi4zOTkyNCAtMi43OTgxMSwzLjM1MTU2IC01LjY0Nzc2LDYuODE0MyAtNi4zMzI1Niw3LjY5NDk4IC0xLjA1MTA3LDEuMzUxNzQgLTAuOTQ0OTUsMi40MDMzOCAwLjY4MTAzLDYuNzQ5MiAxMi40MTExOSwzMy4xNzE4OCAtMTguNjY2MjMsNjcuOTc0OTggLTUyLjg1NTY2LDU5LjE5MjE4IHogTSA2MC41NTc3NTcsNTE4LjE0MjE0IGMgLTI3LjEyMTQxLC02LjgyNzMyIC00Ny42MDkyNCwtMjYuMTA0NDMgLTU2LjUwODcyOTgsLTUzLjE2OTM2IC02LjEyMzc1LC0xOC42MjM0IC01LjE3NDQsLTczLjEzNTg5IDEuOTg4MTgsLTExNC4xNjMyOCBDIDE2LjMzNTk2NywyOTEuODE4MDMgMzguMzgyOTQ3LDIzNi4xNDU2NiA3MC4zODY0MTcsMTg4LjMxNjc4IGMgMjcuMDc5NjYsLTQwLjQ3MDMgNDAuOTc3MjYzLC01My4xNjE4NSA2Ni4xMDUyOTMsLTYwLjM2ODYxIDkuNTQyNjMsLTIuNzM2ODUgMjkuMjgyMTIsLTIuOTE1NzkgMzguNzA3OTcsLTAuMzUwOSAxMy45NzY4MywzLjgwMzI2IDI3LjczMDUyLDExLjY0MDE0IDM2LjY4OTE1LDIwLjkwNTUyIDMuOTY4NDMsNC4xMDQzMSAzNy43MDk1MSw0OS45NjEgMzcuMTQ2OTIsNTAuNDg1NDggLTAuMTMzMjgsMC4xMjQyMyAtMi41NjI2MywtMC4xNTcxNCAtNS4zOTg1NywtMC42MjUyOCAtMTIuMzIwNzMsLTIuMDMzODMgLTI1LjgzNTY3LDIuNzcyNCAtMzYuNzYxNywxMy4wNzMzMyAtMjcuOTM1NDQsMjYuMzM3MiAtNTcuMzY4ODksNzQuNDI0OTkgLTcwLjM4Nzc5LDExNC45OTgxOCAtMTEuNTY2ODYsMzYuMDQ3OSAtMTUuMTI5Nyw1OC43NzI2NSAtMTUuMDY1ODEsOTYuMDkzNzUgMC4wNzIxLDQyLjEzMTA0IDMuNTQ0MDIsNTYuOTA0NTcgMTYuMTQyNCw2OC42ODg4OCAyLjU5MDQ4LDIuNDIzMDkgNi42MzM4MSw1LjM0MDMgOC45ODUxOCw2LjQ4MjY4IDIuMzUxMzcsMS4xNDIzOCA0LjI3NTIyLDIuMzIyNDIgNC4yNzUyMiwyLjYyMjMxIDAsMC4yOTk4OSAtMTIuOTcyNjYsNC43NTA5OCAtMjguODI4MTMsOS44OTEzMSBsIC0yOC44MjgxMjMsOS4zNDYwNyAtMTIuNjU2MjUsMC4yMDk5MiBjIC05Ljk4Njg2LDAuMTY1NjMgLTE0LjE5NTU1LC0wLjE3NzU5IC0xOS45NTQ0MiwtMS42MjcyOCB6IG0gNjkwLjczNTY3MywxLjI4NzkzIGMgLTMuODY5NzcsLTAuNzg1NjcgLTU5LjUwMDY2LC0xOC42NDAyNyAtNTkuNDc4MDMsLTE5LjA4OTMyIDAuMDEzLC0wLjI1NzgxIDIuMTI1MjMsLTEuNDU0NjIgNC42OTM4NSwtMi42NTk1OCA4Ljg4MTY1LC00LjE2NjQ2IDE2Ljk0NzI0LC0xMy43ODc0OSAyMC41Njc0MiwtMjQuNTMzODEgNC4yMzQ3NywtMTIuNTcwNzMgNi4zMzUzOSwtNTYuMjQwOTkgMy44MzI4MywtNzkuNjgxNjEgLTUuNTEzMDIsLTUxLjYzODU3IC0yMS4wMzA2NCwtOTUuNjA2NDcgLTQ4LjU2MTc1LC0xMzcuNTk1NzEgLTEzLjIxNzQ3LC0yMC4xNTg3IC0zNS4wNjg4NiwtNDUuNTgxMzMgLTQzLjg2NjgyLC01MS4wMzYxMSAtNy4wMzMyMSwtNC4zNjA2MyAtMTQuNDM4MSwtNi41MzgwNSAtMjIuNSwtNi42MTYxOSAtNC4xMjUsLTAuMDM5OSAtOC41MTMwMywwLjI1OTA5IC05Ljc1MTE5LDAuNjY0NiAtMS43NDg0NywwLjU3MjYzIC0yLjEzNzA3LDAuNDM5ODcgLTEuNzQwMTQsLTAuNTk0NDkgMC4yODEwNywtMC43MzI0OCA4LjQ0MDk5LC0xMi4yMTg2MiAxOC4xMzMxMywtMjUuNTI0NzcgMTkuMTk5MzEsLTI2LjM1ODMxIDIzLjMwMTM3LC0zMC41NjYzIDM2Ljk1MTk1LC0zNy45MDYyIDI3Ljg1MDQ0LC0xNC45NzUxNSA2Mi45MjI3NywtMTEuNDY1MTQgODcuNDMwNTIsOC43NSAxMi42NTM1NiwxMC40MzcyNSAzNS44NjcwMSw0Mi40MzI2OCA1Mi40OTA3Myw3Mi4zNDg3MyAyNy41MDYzLDQ5LjUwMDM2IDQzLjk0MzI0LDEwMC41OTgxNyA1MS4wNjkzLDE1OC43NjAxNCAxLjMwOTEsMTAuNjg0NzkgMS42NjU1MywyMC43MTU2OCAxLjY2NTYxLDQ2Ljg3NSA5ZS01LDMxLjkzMTY1IC0wLjA4NzIsMzMuNTgyNzkgLTIuMTUzMTcsNDAuNzE3MyAtOC4zMDM3NSwyOC42NzYwOCAtMzEuMzYwOTMsNTAuNDI2MDkgLTU5LjY1MTQ0LDU2LjI2OTY2IC02LjM5NzE1LDEuMzIxMzcgLTI0LjI1MDAzLDEuODQzNyAtMjkuMTMyOCwwLjg1MjM2IHogTSAxNjMuNzI3MTEsNDk0LjIzNDExIGMgLTcuOTcyODUsLTIuOTI4NiAtMTQuNDU1ODMsLTkuMjI0MzkgLTE3LjM2MzQ3LC0xNi44NjIxMSAtMy4zNTcwOSwtOC44MTgzMiAtNi4zNTgxNywtNDQuOTc1NTEgLTUuNTAyMjksLTY2LjI5MTg0IDAuOTg3NzYsLTI0LjYwMDkxIDQuMjg1MTEsLTQ1LjE0OTg5IDEwLjgxNzMzLC02Ny40MTMyNSA5LjA2NTQ0LC0zMC44OTcxOCAyMy4yODAxMSwtNjAuNDY0IDQwLjcwNDIyLC04NC42NjU2NyAxMi41OTcxMSwtMTcuNDk3MDkgMzIuNjA2NDUsLTQwLjA1MTAyIDM5LjI1NzAxLC00NC4yNDkzMyAxOS45NTAwNiwtMTIuNTkzOTIgNDUuMzM5OTEsMi40MDQ5MyA0My42NjA5OSwyNS43OTIzNyAtMC45MjY3OSwxMi45MTAyMyAtOS4zMDAzMiwyMS42NzE0NyAtMjAuNzEyNDYsMjEuNjcxNDcgLTEyLjUyNzMzLDAgLTIxLjczNTI4LC05LjYzMDU4IC0yMS4xNTY0LC0yMi4xMjc0NiAwLjE0NzU1LC0zLjE4NTI5IC0wLjE1NjU2LC01LjU0NTE5IC0wLjczOTYzLC01LjczOTU1IC0yLjI0MTA0LC0wLjc0NzAxIC0yMC4zMzMzLDIwLjU4Mjc1IC0zMi4zODQ1MiwzOC4xNzk1MSAtMzMuNDM1NzgsNDguODIxOCAtNDkuNzc1MTcsMTExLjQwMTk0IC00NC43MTk2NSwxNzEuMjc3MDYgMS4xNjQwOCwxMy43ODY3MiAxLjk0NzI1LDE4LjMxNjkgMy4yMzI4MywxOC43MDAwMSAwLjUwMDQyLDAuMTQ5MTMgMi4wMTM2NSwtMS41NDgzNyAzLjM2MjcyLC0zLjc3MjIyIDguNzc2NjEsLTE0LjQ2NzUzIDI5LjI4MzQ4LC0xMy45MTk0OSAzNi41Mzk4OCwwLjk3NjUzIDUuOTk0NDYsMTIuMzA1NDkgLTEuNDcyNzEsMjguNzE5MTUgLTE1LjQ0MzM2LDMzLjk0NjI1IC02LjEzMTEyLDIuMjkzOTQgLTE0LjIzMDI4LDIuNTMzNDUgLTE5LjU1MzIsMC41NzgyMyB6IG0gNDk3LjkyNDcxLDAuMTgxNzkgYyAtMTguODAwNzksLTcuMDM0MTIgLTI1LjY4MTUzLC0yNy45NzA3NiAtMTMuMjcxMTIsLTQwLjM4MTE3IDkuMzUzOSwtOS4zNTM5IDI1Ljg0MDMyLC03LjAzMjIyIDMyLjY1NjU2LDQuNTk4ODEgMy42Nzg4OSw2LjI3NzU1IDQuMjM4MzgsNS44MTgyMSA1LjU5NDEzLC00LjU5Mjc0IDIuNDYwNDIsLTE4Ljg5MzczIDIuMDQ0MzQsLTUxLjA3NTE2IC0wLjkxNjM4LC03MC44NzYzNiAtNi43MDgzMywtNDQuODY1MDUgLTI0LjMyNzE1LC04Ni44MjExMSAtNTEuNTMyMjMsLTEyMi43MTQ3NCAtOC45ODQ2MiwtMTEuODU0MDYgLTIxLjM2NDQyLC0yNS44MTE1NyAtMjMuMjA5LC0yNi4xNjY4MSAtMS4yMjA3NiwtMC4yMzUxIC0xLjQ1MzE1LDAuNzg2NTQgLTEuMzg1NDIsNi4wOTA4MiAwLjA5MDYsNy4wOTU0NyAtMS44Mzg1LDExLjkxMjQ4IC02LjU2ODQ1LDE2LjQwMTY4IC01LjMxMTMxLDUuMDQwOTkgLTEzLjg2NTU2LDYuODA4MzggLTIxLjAzOTcxLDQuMzQ3MDIgLTEyLjYxNDA5LC00LjMyNzczIC0xOC4zNTA4MiwtMjEuMzM1NzcgLTExLjc0ODI4LC0zNC44MzA4NiA0Ljk1Njk0LC0xMC4xMzE2NCAxNC4wNTMzNywtMTUuODMyNzkgMjUuMzQ3ODQsLTE1Ljg4NjY5IDEwLjQxNDczLC0wLjA0OTcgMTQuMjU3MSwyLjA5NTE4IDI3LjAwODY5LDE1LjA3Njc0IDU0LjgwNzYyLDU1Ljc5NjA3IDg0LjA5NjkyLDEzMy41NTc4NCA3OS40NjQyMiwyMTAuOTczOTEgLTEuMjQwNzIsMjAuNzMzMjUgLTMuNTA0NzgsMzYuNzMyMDggLTYuMDc0MTIsNDIuOTIyMzMgLTEuODg1MTQsNC41NDE3OSAtNy44MTcwMSwxMC41NDE4OSAtMTMuMDYzMTMsMTMuMjEzMzggLTUuNzM1NDQsMi45MjA2NiAtMTUuOTgzNzMsMy44MDAwOSAtMjEuMjYzNiwxLjgyNDY4IHogTSAyNDMuNjM3MTgsNDYyLjU4MjE3IGMgLTE2LjEyMTgxLC01LjUxNjU5IC0yNi43MzE1OCwtMTYuNjUzNDMgLTMxLjQ1Njg1LC0zMy4wMTk1NiAtMS4zMjM4NSwtNC41ODUyMiAtMS41MTkyOSwtNy43OTM1OSAtMS4wNTk4MywtMTcuMzk5MTMgbCAwLjU2MzM1LC0xMS43NzcyNCAtMi44NTgxMywtMS42ODgzMyBjIC0xOS41NjY0NiwtMTEuNTU4MTkgLTI3LjI5MjMzLC0zNi44NTg1OSAtMTcuNjEzMTgsLTU3LjY3ODk2IDMuODI1NjUsLTguMjI5MTcgOC40NzU5OCwtMTMuNjI1NjUgMTUuNzk0MzEsLTE4LjMyODU0IDguNTc3NjgsLTUuNTEyMTkgMTQuODM1ODUsLTcuNDQ2OTMgMjQuNDQyODMsLTcuNTU2NjUgbCA3Ljk2ODc1LC0wLjA5MSA0Ljc1NTEyLC03LjY5NjM4IGMgNi42MTE4MywtMTAuNzAxNTMgMTIuNDU3MzMsLTE2LjM2MjY5IDIxLjQ5NDg4LC0yMC44MTcwMyAxNC4zNDY1OSwtNy4wNzEgMjguMTQzODIsLTYuOTc0NTMgNDIuNjA3MzgsMC4yOTc5NCBsIDcuOTE5ODgsMy45ODIyMiAxNi40NTUxMiwyMi41NTEzOSBjIDI5LjU2Njk5LDQwLjUyMDk0IDUwLjY3Mzg3LDY5Ljc2NjczIDUwLjY3Mzg3LDcwLjIxMzk1IDAsMC44NjUzMiAtNy43ODQ3OCwxMC44Mjg0MyAtOC40NjA4OSwxMC44Mjg0MyAtMC4zODAwMywwIC0xMi4zNjk2OSwtMy43OTY4NyAtMjYuNjQzNzIsLTguNDM3NSAtMTQuMjc0MDMsLTQuNjQwNjIgLTI3LjAwMTQ0LC04LjQzNzUgLTI4LjI4MzE0LC04LjQzNzUgLTMuMDc2MzUsMCAtNy4zOTAyMiwyLjI5MDM4IC05LjIxMTU5LDQuODkwNzQgLTEuODI5MjMsMi42MTE1OSAtMS44ODg5Niw4LjQ0MTQ2IC0wLjEyMTUzLDExLjg1OTI5IDEuNzM2MTcsMy4zNTczOSAzLjgwNTIxLDQuMjE2OTUgMzMuMDM3NzUsMTMuNzI1MjkgbCAyNC41MzU2Myw3Ljk4MDU5IDAuMzA4MTIsNy4wMjI0MiAwLjMwODEyLDcuMDIyNDIgLTIwLjYyNSw2LjY1NjA0IGMgLTExLjM0Mzc1LDMuNjYwODIgLTM1LjQ4NzIzLDExLjQ2NTM0IC01My42NTIxOSwxNy4zNDMzOCAtMzcuMDUyMDMsMTEuOTg5NzMgLTM5LjU5MDQ5LDEyLjQxNjUgLTUwLjg3OTA2LDguNTUzNzUgeiBtIDMyNy42NTYyNSwtMS4xNTU5MiBjIC01LjE1NjI1LC0xLjcyNzggLTI0LjU2MjUsLTguMDQ3OTIgLTQzLjEyNSwtMTQuMDQ0NzEgLTE4LjU2MjUsLTUuOTk2NzcgLTM4LjI1NzAxLC0xMi4zNzk5OSAtNDMuNzY1NTcsLTE0LjE4NDkyIGwgLTEwLjAxNTU4LC0zLjI4MTcgMC4xMzE2NywtNi44ODM0MSAwLjEzMTY2LC02Ljg4MzQxIDIzLjQ3NzY3LC03LjYxNTk2IGMgMjkuNjI4MDQsLTkuNjExMSAzMS4yOTk5NSwtMTAuMjgwNzEgMzMuNjkzNjgsLTEzLjQ5NDUxIDMuMDk0MjksLTQuMTU0MzYgMi43MDYxNiwtMTAuMTc2MTMgLTAuODg3NTEsLTEzLjc2OTgxIC00Ljk5NTU3LC00Ljk5NTU2IC02LjU1OTg5LC00Ljc5Mjk4IC0zNS42NjczNyw0LjYxODgzIC0xNC40ODYzNyw0LjY4NDEzIC0yNi43MjA3NCw4LjUwMDU5IC0yNy4xODc1LDguNDgxMDIgLTAuNDY2NzYsLTAuMDE5NiAtMi4xMTQyOCwtMS43NzQyNyAtMy42NjExNSwtMy44OTkzMyAtMS41NDY4OCwtMi4xMjUwNyAtMy4zMTc0NCwtNC41MzQ4NCAtMy45MzQ1OCwtNS4zNTUwNSAtMC45NDQ0MiwtMS4yNTUxOCAzLjk5MjgxLC04LjU0MTc1IDMxLjE4MzkzLC00Ni4wMjI1NCAxNy43NjgzLC0yNC40OTIxOSAzMy40MTA5NiwtNDUuNzEyNTIgMzQuNzYxNDYsLTQ3LjE1NjI5IDUuNzk5NDcsLTYuMjAwMDUgMTguMjA0MiwtMTAuMzk5MTcgMzAuMzMyOTQsLTEwLjI2Nzk5IDE4LjQ2MDM0LDAuMTk5NjUgMzEuMjA5NjksOC4wMjg4MiA0Mi4xNjQ1OCwyNS44OTI1NyBsIDQuODcwNTQsNy45NDIyMSA0Ljg0MTgxLC0wLjQ5MTc0IGMgMTEuMDE1MDMsLTEuMTE4NzIgMjMuODgzNTMsMy42Njk0NSAzMy4zMDUzNSwxMi4zOTIzOSAyMC45MTg3LDE5LjM2NzAyIDE4LjA2OTI5LDU0LjYzNTczIC01LjY1NjE0LDcwLjAwOTI5IGwgLTQuNzUyNTQsMy4wNzk1NCAwLjYzOTc2LDEwLjM4OTAzIGMgMC43NDE4LDEyLjA0NTk2IC0wLjU4OTEsMTkuNTkzMTYgLTQuOTg4NjQsMjguMjg5MTMgLTcuNzI1MTQsMTUuMjY5MjcgLTI0LjE2NjYsMjUuNjY0NCAtNDAuMjg5MSwyNS40NzI4NCAtNC40MjM5NSwtMC4wNTI2IC04Ljk0NjQ3LC0wLjk4NDQ4IC0xNS42MDQzNywtMy4yMTU0OCB6IG0gLTE1Ny45Njg3NSwtNC41NzY1OSBjIC0xMS4wNzEwMiwtMi40NjE1NiAtMTkuNjM4OTcsLTkuNDI5MjcgLTI0LjY4MDI1LC0yMC4wNzA3NCAtMi42OTMzMywtNS42ODUyMiAtMi45NzYsLTcuMTI3ODkgLTIuOTc2LC0xNS4xODgxNyAwLC03LjcwNzU1IDAuMzM5MTcsLTkuNjI5OTQgMi41MjAwMiwtMTQuMjgzMjQgNS4wMTA5LC0xMC42OTE4MiAxMS43MTgwOCwtMTYuODIzOTEgMjIuMzMyLC0yMC40MTcyMSA3LjQ3ODMxLC0yLjUzMTc1IDE2LjQ5NDU2LC0yLjE5Nzg4IDI0LjYzMzUyLDAuOTEyMTcgNi45NDI0NiwyLjY1Mjg1IDE1LjY4NzYxLDEwLjYyNiAxOC45MzUwNCwxNy4yNjM1MSAxMC41ODEwNCwyMS42MjY4NSAtMi4zNTY0OCw0Ny43MTA1NyAtMjUuODc2ODYsNTIuMTcxMTEgLTUuOTY1NTUsMS4xMzEzNCAtOC4zMzM4NywxLjA2OTcxIC0xNC44ODc0NywtMC4zODc0MyB6IG0gLTE3LjUwODc5LC04NS4xNjI3OCBjIC0xLjA2MjU5LC0xLjE3MDA1IC0xMC45MTY3NywtMTQuNTcyNjkgLTIxLjg5ODE5LC0yOS43ODM2MyAtMTAuOTgxNDIsLTE1LjIxMDk0IC0yMi43NjMzOSwtMzEuNDUzMTIgLTI2LjE4MjE1LC0zNi4wOTM3NSAtMTguNzIxOTksLTI1LjQxMzE5IC0xOC45Njg1LC0yNS44NzAwMyAtMjAuMjM0MTcsLTM3LjUgLTEuOTA3MDUsLTE3LjUyMzQ2IDkuNjQxNTksLTM3Ljc1MjA5IDI2LjEzNjMzLC00NS43ODA1IDMuNjk1MDMsLTEuNzk4NDUgOC4xOTQ3OCwtMy41NDc5MSA5Ljk5OTQ3LC0zLjg4NzY4IDEuODA0NjksLTAuMzM5NzcgNS40NDE5MiwtMS4yMTc0MyA4LjA4MjczLC0xLjk1MDM1IGwgNC44MDE0OCwtMS4zMzI1OSAyLjA5MDY1LC02LjUwMTkxIGMgNS40NDc0NiwtMTYuOTQxNjYgMTkuMTQzNTEsLTI4LjQ3MTE3IDM2Ljk3MTAyLC0zMS4xMjI2OCA4LjM2NDM1LC0xLjI0NDA0IDE4LjQ1OTg5LDAuNDMxNTMgMjYuNjAyMjgsNC40MTUyMyAxMC4wNjA2Nyw0LjkyMjIzIDIwLjM5NzksMTcuNzUzOTQgMjIuODQ1NzcsMjguMzU4NzEgMS4yMzc4NSw1LjM2MjYzIC0wLjA3MzksNC41OTU4MyAxMy45MTg1Nyw4LjEzNjQ0IDIxLjg1NTQ2LDUuNTMwMjQgMzYuNTA4MDcsMjMuNzU4NTkgMzYuNTMxNiw0NS40NDY1OCAwLjAxNTgsMTQuNTg2MDMgMC45MzkzOCwxMi45NTQwMyAtMzYuMTI0NzIsNjMuODM0OTMgLTI1LjA0NDYzLDM0LjM4MDggLTMzLjg4NDA2LDQ1Ljg2ODIyIC0zNS4wMDMyOCw0NS40ODkwNSAtMC44MjM1NCwtMC4yNzkgLTMuNjg2NzgsLTEuMjYwNTcgLTYuMzYyNzYsLTIuMTgxMjYgbCAtNC44NjU0LC0xLjY3Mzk3IC0wLjI5MDg1LC0yOS4wNjI1IGMgLTAuMjgzMjUsLTI4LjMwMzQ5IC0wLjM0NTI5LC0yOS4xMzg4NCAtMi4zNzU4OSwtMzEuOTg1NTYgLTQuMjE3MTgsLTUuOTEyMTIgLTExLjcxNTgsLTYuNDYwNDQgLTE2LjczNTExLC0xLjIyMzcyIGwgLTIuNzQyMzQsMi44NjExMyAtMC4yNzU3OSwyOS43MDUzMiAtMC4yNzU4MSwyOS43MDUzMyAtNS4zNDkxOSwxLjczNjU3IGMgLTIuOTQyMDcsMC45NTUxMSAtNS43OTU0LDEuOTEyNDQgLTYuMzQwNzUsMi4xMjczOCAtMC41NDUzNCwwLjIxNDk1IC0xLjg2MDkyLC0wLjU2NjUgLTIuOTIzNSwtMS43MzY1NyB6IE0gMjkyLjI3NjgyLDIyNi4yMzM5NiBjIC03Ljc1MzgsLTIuNzcwODIgLTEzLjAzMzA5LC03LjQyOTQ4IC0xNy4wMDE0NiwtMTUuMDAyNzcgLTIuODA4MDgsLTUuMzU4OTYgLTIuODU1MjEsLTE3LjAzNDUyIC0wLjA5MzQsLTIzLjEyNTU3IDMuNTYzMjQsLTcuODU4NDEgNy4xNTI5MSwtMTAuODUxNiAyMS44MjI0MiwtMTguMTk2MzQgNzAuMjc2MzQsLTM1LjE4NTk2IDE1My4zOTA4NCwtMzguOTAyNzIgMjI2LjQ3NjQ4LC0xMC4xMjc3IDE3LjgxNDc4LDcuMDEzOTggMzQuMzIyODcsMTUuNDEzMjggMzguNDk2NjcsMTkuNTg3MDkgNy43MjgyLDcuNzI4MjEgMTAuMDc4MTcsMTkuNzkzMTcgNS45ODU3MSwzMC43MzEyNiAtMi4zODE1Nyw2LjM2NTMgLTkuOTgzNjEsMTMuNzA1MjcgLTE2LjQ5MTEsMTUuOTIyNiAtMTkuNTYyNTQsNi42NjU2NCAtMzcuMjgyODgsLTkuOTg5NzYgLTI5LjMxODc1LC0yNy41NTY3OCAzLjI4ODgsLTcuMjU0MzIgNy42OTk0MSwtMTAuNzU1MDkgMTUuMTUzNTUsLTEyLjAyNzYxIDIuMTExNSwtMC4zNjA0NiA0LjAwNjA2LC0xLjE1NjMyIDQuMjEwMTUsLTEuNzY4NTcgMC40NDA2NiwtMS4zMjE5OCAtNy4zMTkyOSwtNS4zNjA5IC0yMS4xMzIxNiwtMTAuOTk4OTEgLTM2LjMwODMsLTE0LjgyMDAzIC04MS4xOTAzLC0yMS43MDU3MiAtMTE5LjI0Nzc3LC0xOC4yOTQ3MSAtMzEuMzEwNTMsMi44MDYzMSAtNTkuMzc4MzMsOS45MDQwNiAtODcuMDg0MTksMjIuMDIxNzggLTExLjMyNTkzLDQuOTUzNjMgLTE0LjU0MTM5LDcuMzYzNzcgLTExLjExODk0LDguMzM0MTMgMC42NDQ1NCwwLjE4MjczIDIuOTcxODQsMC44MjEzNCA1LjE3MTgsMS40MTkxMSA4LjQ1NDg2LDIuMjk3MzYgMTQuMjk1NjUsMTAuMjc2MDMgMTQuMjYwNzQsMTkuNDgwNTYgLTAuMDM0NSw5LjA5MDA5IC00LjY5NzkzLDE2LjIyMDYxIC0xMi44Mzk5MiwxOS42MzI1NCAtMy43Nzk0LDEuNTgzNzYgLTEyLjc3NzU3LDEuNTY4MDYgLTE3LjI0OTg1LC0wLjAzMDEgeiBNIDI0NS45NjQ3MywxNjUuODM3MSBjIC0yNS4yNzU3OSwtMzQuNzUwNTUgLTI3LjE1NjksLTM5LjE0NTIzIC0yNy4xNjU4MSwtNjMuNDY1MSAtMC4wMDcsLTE3LjQxMjY5NCAxLjMwMjIxLC0yMy4wNDIwMTQgOC43MTcyMiwtMzcuNTAwMDA0IDMuNDk0MzIsLTYuODEzMzEgNi4wNDg5NSwtMTAuMTcwNTYgMTMuMjcxMDQsLTE3LjQ0MDU2IDExLjAyNDE5LC0xMS4wOTczMSAxNy41NTA5MSwtMTUuMDIyMTcgMzYuMzY2MDEsLTIxLjg2ODc2IDcwLjg0MjI1LC0yNS43Nzg2NjA0IDE0NS44Mjk1MSwtMzIuMTQyNDUwNCAyMjAuNTQ2NDksLTE4LjcxNjY3MDQgMjguNzE2ODksNS4xNjAwOTA0IDY4Ljc0NDc0LDE3LjI2NDE0MDQgODUuMzgyNTksMjUuODE4OTAwNCAxOC45MjI1MSw5LjcyOTQ4IDMzLjI0OTYzLDI3LjU1Mjc0IDM5LjQ4NTYxLDQ5LjEyMTAyIDEuODAyMzMsNi4yMzM2NyAyLjE1MjcsOS42MjAyNCAyLjEyOTc4LDIwLjU4NjA3NCAtMC4wMzEsMTQuODMwNzEgLTEuNzk0MSwyMy4wMzE4MyAtNy4yNDE1LDMzLjY4MzkyIC0zLjEzNTg1LDYuMTMyIC0zNi4yNDAxNCw1Mi45Mjc0MSAtMzcuNDkwODYsNTIuOTk2MTggLTAuMzg2NzEsMC4wMjEzIC0wLjcwMzEyLC0xLjE4OTM5IC0wLjcwMzEyLC0yLjY5MDMzIDAsLTguNDY5OTMgLTcuNzM4NywtMjIuNjE4OCAtMTUuNzE1MTEsLTI4LjczMjM4IC01LjQxMzM4LC00LjE0OTEyIC0yMS40NjMzNywtMTEuOTMzNjIgLTM1LjM3ODY0LC0xNy4xNTkyMSAtNDUuNTYzNjQsLTE3LjExMDQ3IC05NS43NDA5NCwtMjMuMjc5MjYgLTE0Mi4wMzEyNSwtMTcuNDYxMjkgLTM0LjA4NDg1LDQuMjgzOTIgLTY5LjgxOTM4LDE0Ljg5MDYzIC05Ni43MTkyNiwyOC43MDgxNiAtMTQuMDM0MDUsNy4yMDg3OSAtMjEuNjgyLDE2LjY0ODM4IC0yNS4xMTIyMiwzMC45OTUwNSBsIC0xLjUwMDk1LDYuMjc3NjEgLTE2Ljg0MDAyLC0yMy4xNTI2MSB6Ii8+Cjwvc3ZnPg=="
                ]
            },
            "alternate": 1
        },
        "colours": [
            {
                "R": 0,
                "G": 0,
                "B": 0,
                "A": 1
            },
            {
                "R": 255,
                "G": 215,
                "B": 0,
                "A": 1
            }
        ],
        "output": {
            "resolution": 2500,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {
                    "shape-rendering": "crispEdges",
                    "transform-origin": "top left"
                }
            }
        }
    }
    ```

    <div markdown="span" style="display: flex; justify-content: space-between;">
        <figure style="width: 100%; text-align: center;">
            ![banner.png](./images/yabure_seigaiha_image.png){ width="75%" height=auto }
            <figcaption style="margin-top: 5px;"><code>output/yabure_image_seigaiha.png</code></figcaption>
        </figure>
    </div>

    !!!tip

        * You can use the created single SVG polygon file to create a compatible SVG for your Yabure Seigaiha pattern.
        * Use `base64 vector-image.svg` to get base64 string, or write to temporary file with `cat vector-image.svg | base64 -w 0 > vector-image_base64.txt` and copy-paste the contents into the `images` key in the JSON preset.
        * You can use [https://jakearchibald.github.io/svgomg/](https://jakearchibald.github.io/svgomg/) to simplify predefined SVGs, making them more likely to work when creating a broken pattern with substituted images.


### Options

???+ example "`input/custom.json`"

    You can fully customise the settings to your liking.

    - `seed` - `int` - The seed for the [pseudo-random numbers generator](https://docs.python.org/3/library/random.html). If not set defaults to `None` which uses the current time as the seed.
    - `fractions` - `int` - The number of fractions of the polygon (including outer side of polygon).
    - `edges` - `int` - The number of sides of the polygon.
    - `spacing` - `float`|`int` - A factor for spacing between the fractions inside the polygon. 0 denotes equal distance between alternating fractions.
    - `rotation` - `float`|`int` - The rotation of the polygon in degrees.
    - `pattern` - `dict`|`bool` - Settings for the Seigaiha pattern.
        - `horizontal` - `dict` - Settings for the horizontal pattern.
            - `amount` - `int` - The number of horizontal polygons.
            - `spacing` - `float`|`int` - A factor for spacing between the horizontal polygons.
        - `vertical` - `dict` - Settings for the vertical pattern.
            - `amount` - `int` - The number of vertical polygons.
            - `spacing` - `float`|`int` - A factor for spacing between the vertical polygons.
        - `broken` - `dict` - Settings for the broken pattern.  
            - `factor` - `float`|`int` - The factor denoting how many polygons should be broken in the entire pattern.
            - `factor_rounding` - `str` - The rounding method for the `factor`. Options: `ceil`, `floor`, `round`. This options rounds the amount of broken polygons for the pattern.
            - `fractions` - `int` - The number of fractions of the polygon (including outer side of polygon).
            - `skip_edge` - `bool` - Denotes if broken polygons should be skipped on the edge of the pattern.
            - `colours` - `list` - A list of dictonaries of RGB(A) colours to use.
            - `images` - `list` - A list of base64 strings of SVG images to use.
        - `alternate` - `int` - Denotes if lines should alternate or not. `1` for alternate, 0 for not alternate. Defaults to `1`. 
    - `colours` - `list` - A list of dictonaries of RGB(A) colours to use.
    - `output` - `dict` - Settings for the output images.
        - `resolution` - `int` - The resolution denoting either max width or max height of desired output image.
        - `svg` - `dict` - Settings for the SVG output.
            - `preserveAspectRatio` - `str` - The SVG tag option to [preserve aspect ratio](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/preserveAspectRatio).
            - `style` - `dict` - The style of polygons.
                - `shape-rendering` - `str` - The [shape rendering](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/shape-rendering) style for the polygons.

