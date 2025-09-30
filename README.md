# webapp_mangetamain

[![PyPI - Version](https://img.shields.io/pypi/v/webapp-mangetamain.svg)](https://pypi.org/project/webapp-mangetamain)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/webapp-mangetamain.svg)](https://pypi.org/project/webapp-mangetamain)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation
### Setup 
Project tree structure
```
webapp_mangetamain/
├── data/                # CSV files
├── src/
│   └── webapp_mangetamain/
│       ├── __init__.py   
│       └── .... 
└── tests/                 
├── LICENSE.txt
├── README.md
├── pyproject.toml         # Project config
```

```console
# dev
hatch env create
hatch shell
hatch run webapp

# utils cmd
hatch env remove default
hatch env create

```

## License

`webapp-mangetamain` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
