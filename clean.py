import argparse, sys, json

import termcolor as t

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Remove duplicates and escape characters from JSON file', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython clean.py followers.json\n"
    )
parser.add_argument("input", metavar="input", help="[REQUIRED] JSON file to clean")
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

followers, names = {}, {}
count, removed = 0, 0
for index in data["followers"].items(): 
    if index[1]["name"] not in names.values():
        followers[count] = index[1]
        names[count] = index[1]["name"]
        count += 1
    else:
        removed += 1

# Remove unicode escapes

for index in followers.items():
    index[1]["name"] = index[1]["name"].encode("utf-8").decode("utf-8")
    index[1]["bio"] = index[1]["bio"].encode("utf-8").decode("utf-8")

data["followers"] = followers
filejson.truncate(0)
filejson.seek(0)
json.dump(data, filejson, indent=4)
print(t.colored("Removed "+str(removed)+" data","green")) 