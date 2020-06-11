import argparse, sys, json

import termcolor as t

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Remove duplicates and escape characters from JSON file', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython clean.py followers.json followers name\n"
    )
parser.add_argument("input", metavar="input", help="[REQUIRED] JSON file to clean")
parser.add_argument("column", metavar="column", help="[REQUIRED] Column name to clean")
parser.add_argument("variable", metavar="variable", help="[REQUIRED] Unique variable name to clean")
args = parser.parse_args()
inputjson = args.input
if  inputjson.find(".json") == -1:
    if inputjson.find("."):
        inputjson = inputjson.split(".")[0] + ".json"
        print(t.colored("Non json file given as output format. Changing to " + inputjson, "yellow"))
    else:
        inputjson = inputjson + ".csv"

# Open JSON

try:
    filejson = open(inputjson,"r+")
    data = json.load(filejson)
except FileNotFoundError:
    sys.exit(t.colored("File name " + inputjson + " not found !","red"))  

# Remove duplicates

clean, variable = {}, {}
count, removed = 0, 0
for index in data[args.column].items(): 
    if index[1][args.variable] not in variable.values():
        clean[count] = index[1]
        variable[count] = index[1][args.variable]
        count += 1
    else:
        removed += 1

data[args.column] = clean
filejson.truncate(0)
filejson.seek(0)
json.dump(data, filejson, indent=4)
print(t.colored("Removed "+str(removed)+" data","green")) 