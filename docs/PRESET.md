# Presets

* [Examples](#examples)
* [Configure](#configure)

## Examples

### 9 edges
```json
{
    "width": 2500,
    "fractions": 11,
    "edges": 9,
    "spacing": 0.3,
    "rotation": 0,
    "pattern": true,
    "repeat": {
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
            "fractions": 4,
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
    ]
}
```

### 7 edges

```json
{
    "width": 2500,
    "fractions": 9,
    "edges": 7,
    "spacing": 0.25,
    "rotation": 0,
    "pattern": true,
    "repeat": {
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
    ]
}
```

## Configure

There are several options that can be configured for a preset