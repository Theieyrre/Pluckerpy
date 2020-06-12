![pluckerpy](img.png)

 # Twitter Web Scrapping Tool with Selenium & Chrome Web Driver

## Requirements
> Python 3 ( 3.8.3)\
> Chrome Browser ( Version 83 )

## Install

If you have pipenv installed run to install dependencies and create virtualenv 
```
pipenv install
pipenv shell
```

To install dependencies with pip without virtualenv 
```
pip install -r requirements.txt
```

## Run 

### Search Scraping
```
python search.py github 50 test
```
| Parameters   |      Description      |
|----------|:-------------:|
| input |  [REQUIRED] Topic word, to seach in twitter|
| min |    Minimum tweet count  |
| output | Output file name to write csv |
| -b, --browser | Option to open Chrome window |
| -t, --threshold | Threshold to write to output file |

### Profile Scraping
```
python profile.py github 50 test
```
To get all tweets of a user, set min to -1

| Parameters   |      Description      |
|----------|:-------------:|
| input |  [REQUIRED] Name of profile without @ |
| min |    Minimum tweet count  |
| output | Output file name to write json |
| -b, --browser | Option to open Chrome window |
| -t, --threshold | Threshold to write to output file |

### Followers Scraping
```
python followers.py pluckerpy password123 github 50 test
```

To get all followers of a user, set min to -1

| Parameters   |      Description      |
|----------|:-------------:|
| username |  [REQUIRED] Username of a valid Twitter Account |
| password |  [REQUIRED] Password of a valid Twitter Account |
| input |  [REQUIRED] Name of profile without @ |
| min |    Minimum tweet count  |
| output | Output file name to write json |
| -b, --browser | Option to open Chrome window |
| -t, --threshold | Threshold to write to output file |

### Remove duplicates
```
python clean.py followers.json followers name
```
| Parameters   |      Description      |
|----------|:-------------:|
| input |  [REQUIRED] JSON file to remove duplicates |
| column |  [REQUIRED] Column name to remove duplicates |
| variable |  [REQUIRED] Unique variable of rows |

### Label Data
```
python data.py
```

Write and update are mutually exclusive, can't be used together
| Parameters   |      Description      |
|----------|:-------------:|
| -w, --write |  [DEFAULT] Create JSON file and write it |
| -u, --update |  Update existing labeled JSON file |
| filename |  Output file name to write json, default name <account name>.json |
