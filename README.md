# pychromedriver
## Installation:
```
# From PyPI
pip install pychromedriver
```
## Usage:
```
from selenium import webdriver
from pychromedriver import chromedriver_path

bs = webdriver.Chrome(executable_path=chromedriver_path)
bs.get('https://www.pypi.org')
```
