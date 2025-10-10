# Webapp Mangetamain

A lightweight web application project for data-driven workflows on Recipe from [Kaggle](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions).  

---

## 📑 Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Interface](#interface)
- [License](#license)

---

## 🛠️ Prerequisites

[![Python](https://img.shields.io/badge/Python->=3.10-blue?logo=python&logoColor=white)](https://www.python.org/)

Make sure you have **Python 3.10 or higher** installed.

---

## ⚙️ Installation

### Setup  

Clone the repository and set up the environment using [Hatch](https://hatch.pypa.io/):  

```console
# Create development environment
hatch env create

# Enter shell
hatch shell

# Run the webapp
hatch run webapp

# Utilities
exit
hatch env remove default
hatch env create
```

#### Create matrix
in a folder artifacts

create `co_occurence.csv` and `jaccard.csv` with 

...



## 📂 Project Structure

```
webapp_mangetamain/
├── data/                   # CSV files
├── artifacts/              # create CSV with ingredient_data_process.py
├── src/
│   └── webapp_mangetamain/
│       ├── __init__.py   
│       └── ...
├── tests/                  
├── LICENSE.txt
├── README.md
├── pyproject.toml          # Project config
```
test :
```
hatch run test # unit test
hatch run lint # pep8...
```
---

## 🖥️ Interface

*(Add screenshots, UI descriptions, or usage instructions here)*
## dev
```
http://localhost:8501
```

![CI](https://github.com/Ambroise012/webapp-mangetamain/actions/workflows/ci.yml/badge.svg)


## Deployement

Dockerfile


