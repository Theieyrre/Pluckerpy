# ScrapTweett

Twitter Web Scrapping Tool with Selenium & Chrome Web Driver

## Requirements
> Python 3 ( 3.8.3)\
> Chrome Browser ( Version 83 )

## Install

If you have pipenv installed run to install dependencies and create virtualenv 
> pipenv install
> pipenv shell

To install dependencies with pip without virtualenv 
> pip install -r requirements.txt

## Run 

### Search Scraping

> python search.py github 50 test

| Parameters   |      Description      |
|----------|:-------------:|
| input |  [REQUIRED] Topic word, to seach in twitter|
| min |    Minimum tweet count  |
| output | Output file name to write csv |
| -b, --browser | Option to open Chrome window |
| -t, --threshold | Threshold to write to output file |

