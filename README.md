# UK Power Demand Data Analysis
## About this Repository
This repository aims to create a simple dash application that has two tabs:
* Table Tab: To browse any dataset interactively using dash that provides pagination
* Charts Tab: This tab enables users to create interactive charts from the data read above.

This code directory consists of 2 types of files
1. .py files : Contains code to run the application and clean the data needed 
2. .ipynb files : Contains code samples along with self-explanatory text and visualizations to explain power demand as a function of temperature

## How to run .py files

First, clone this repository and open a terminal inside the root folder.

Create and activate a new virtual environment (recommended) by running the following:

```
python3 -m venv myvenv
source myvenv/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```

Run the app:

```
python dash-app.py
```

Open a browser page at [http://127.0.0.1:8050](http://127.0.0.1:8050)

## 
