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
| -c, --click | Option to open tweet on new tab to get location |
|-w, --waitlong | Option to wait more than 10 seconds on loading elements.<br>Will reduce runtime significantly ! Use only have slow connection |

### Profile Scraping
```
python profile.py github 50 test
```
To get all tweets of a user, set min to -1  
username and password arguments are used for getting total number of tweets. They are non-optional even without -1 tweet count

| Parameters   |      Description      |
|----------|:-------------:|
| username |  [REQUIRED] Username of a valid Twitter Account |
| password |  [REQUIRED] Password of a valid Twitter Account |
| input |  [REQUIRED] Name of profile without @ |
| min |    Minimum tweet count  |
| output | Output file name to write json |
| -b, --browser | Option to open Chrome window |
| -t, --threshold | Threshold to write to output file |
| -c, --click | Option to open tweet on new tab to get location |
| -s, --seperator | Seperator for csv file |
|-w, --waitlong | Option to wait more than 10 seconds on loading elements.<br>Will reduce runtime significantly ! Use only have slow connection |

### Followers Scraping
```
python followers.py pluckerpy password123 github 50 test
```

To get all followers of a user, set min to -1  
username and password arguments are used for getting total number of follower. They are non-optional even without -1 follower count

| Parameters   |      Description      |
|----------|:-------------:|
| username |  [REQUIRED] Username of a valid Twitter Account |
| password |  [REQUIRED] Password of a valid Twitter Account |
| input |  [REQUIRED] Name of profile without @ |
| min |    Minimum tweet count  |
| output | Output file name to write json |
| -b, --browser | Option to open Chrome window |
| -t, --threshold | Threshold to write to output file |
| -c, --click | Option to open follower on new tab to get location |
|-w, --waitlong | Option to wait more than 10 seconds on loading elements.<br>Will reduce runtime significantly ! Use only have slow connection |
|-l, --load | Option to load json file with names to continue after reaching rate limit |

### Remove duplicates
```
python clean.py followers.json followers name
```
clean.py will return UnicodeDecodeErro if another application is used to change unicode escape characters  
variable and spaces are mutually exclusive, can't be used together  
concat.py remove duplicates across multiple jsons  
Doesn't work on lists, dictionaries only

| Parameters   |      Description      |
|----------|:-------------:|
| input |  [REQUIRED] JSON file to remove duplicates |
| column |  [REQUIRED] Column name to remove duplicates |
| -v, --variable |  Unique variable of rows |
| -s, --spaces |  Option to remove space characters from content |

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

### Concatenate JSON Files
```
python concat.py directory_of_jsons
```

If file name has whitespace, type it inside quote marks
| Parameters   |      Description      |
|----------|:-------------:|
| directory |  Directory path with json files |
| -o, --output |  Output file name to concat all, default output.json |
| -v, --verbose |  Extra prints with weights and counts |