# Benchmarking table markdown tool

This is a python script for creating markdown tables from benchamarking test results.

## Introduction

This simple script allows you to convert properly formatted JSON or python files into a markdown report that compares all the computers in the data set. It is completely redundant and basically it only exists because it made a college assignment easier for me (that and my love for python and markdown).

## Requirements

The script requires at least [Python 3.6](https://www.python.org/downloads/release/python-364/) as it uses the [PEP 498](https://www.python.org/dev/peps/pep-0498/) specification.

The script uses [click](http://click.pocoo.org), a beautiful utility for creating even more beautiful command-line applications. Make sure you have it installed by typing:

```bash
$ pip install click
```

## Installation

To test the script, you can make a new virtualenv and then install the package:

```bash
$ virtualenv venv
$ . venv/bin/activate
$ pip install --editable .
```

Afterwards, the table command should be available:

```bash
$ table --demo p --output demo.md
```

## Input files

This script can load JSON and python files.

(###JSON)

The following shows an example of a valid json file:

```json
[
    "Time of excecution in seconds",
    ["Computer", "mafft", "mrbayes"],
    {
        "A": [18.95, 42.51],
        "B": [20.81, 49.69]
    },
    "LIB"
]
```

Note that the script expects an array with the following elements:

1. The title of the data set. (A String)
2. The headers of the table in a list. Note that "Computer" is always the first column.
3. The data set as a dictionary that maps each computer to its respective test scores.
4. The type of data the script will be dealing with. Either:
    - **LIB** Lower is better, or
    - **HIB** Higher is better.

The previous example would produce the following output:

```markdown
# Time of excecution in seconds

We have the following data:

| Computer | mafft | mrbayes |
| :---: | :---: | :---: |
| A | 18.95 | 42.51  |
| B | 20.81 | 49.69  |

## With computer A as reference

The normalized data looks like this

| Computer | mafft | mrbayes |
| :---: | :---: | :---: |
| A | 1.00 | 1.00  |
| B | 0.91 | 0.86  |

If we order their geometric means in increasing order, we have that:

- Computer B is 0.88 times as fast as computer A.

## With computer B as reference

The normalized data looks like this

| Computer | mafft | mrbayes |
| :---: | :---: | :---: |
| A | 1.10 | 1.17  |
| B | 1.00 | 1.00  |

If we order their geometric means in increasing order, we have that:

- Computer A is 1.13 times as fast as computer B.
```

### Python

The following shows an example of a valid python data file:

```python
#!/usr/bin/python3
# Example data.py file
(
    # Title
    "Time of excecution in seconds",
    # Headers
    ["Computer", "mafft", "mrbayes"],
    # Test results for each computer
    {
        "A": [18.95, 42.51],
        "B": [20.81, 49.69]
    },
    # Type of data (LIB | HIB)
    "LIB"
)
```

So if you're planning on using a python file instead, note that the script expects a tuple that contains:

1. The title of the data set. (A String)
2. The headers of the table in a list. Note that "Computer" is always the first column.
3. The data set as a dictionary that maps each computer to its respective test scores.
4. The type of data the script will be dealing with. Either:
    - **LIB** Lower is better, or
    - **HIB** Higher is better.

The previous example would produce the same output as the [JSON](#JSON) example.

## Usage

```help
Usage: table [OPTIONS]

Options:
  --demo TEXT    selects a demo accepts "p" or "t"
  --load TEXT    loads the specified json or py file
  --new TEXT     creates a new data set with the provided title
  --output TEXT  saves output to the specified file
  --help         Show this message and exit.
```

## Acknowledgements

Test results in the examples were produced using [the Phoronix Test Suite](http://www.phoronix-test-suite.com/) a really cool benchmarking tool.