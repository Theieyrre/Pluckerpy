# ScrapTweett

Twitter Web Scrapping Tool with Selenium & Chrome Web Driver

## Requirements
> Python 3 ( 3.8.3)\
> Chrome Browser ( Version 83 )\

## Install

If you have pipenv installed run to install dependencies and create virtualenv 
> pipenv install
> pipenv shell

To install dependencies with pip without virtualenv 
> pip install -r requirements.txt

## Run 
> python app.py github 50 test

## Parameters
  >input&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;[REQUIRED] Topic word, to seach in twitter\
  >min&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Minimum tweet count, default 100\
  >output&ensp;&ensp;&ensp;&ensp;Output file name to write tsv, default\ name output.tsv