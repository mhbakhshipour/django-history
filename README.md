# Django History


## Getting started

This repository contains a utility class WithLogModel that can be inherited to add a histories field to log changes in fields when using a model.

## Introduction

When working with models, it can be useful to keep track of changes in the model's fields over time. The WithLogModel utility provides a simple way to add a histories field to your model, which stores the changes made to the model's fields.

## Installation

```
clone the project
```

## Usage

To use the WithLogModel utility, follow these steps:

1. Import the WithLogModel class into your project:
```
from utils.with_log_model import WithLogModel
```
2. Inherit the WithLogModel class in your model class:
```
class MyModel(WithLogModel):
    pass

```
3. Access the histories field to view the log of changes:
```
model_instance.histories -> value:
[
    {
        "editor": {
            "id": null,
            "avatar": null,
            "username": "system",
            "full_name": "system"
        },
        "next_data": {
            "field_a": [
                "test2 - 2023-03-06 07:33:45.657857+00:00"
            ]
        },
        "change_date": "2023-06-03 11:03:52.194451",
        "previous_data": {
            "field_a": [
                "test - 2023-03-06 07:33:45.657857+00:00"
            ]
        }
    }
]
```

## Contributing

Contributions to this repository are welcome. If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.
