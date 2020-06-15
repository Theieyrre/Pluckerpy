import argparse, sys, json

import termcolor as t
import pandas as pd

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Remove duplicates and escape characters from JSON file', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython clean.py followers.json followers name\n"
    )
parser.add_argument("input", metavar="input", help="[REQUIRED] JSON file to clean")
parser.add_argument("column", metavar="column", help="[REQUIRED] Column name to clean")
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--variable", metavar="variable", help="[REQUIRED] Unique variable name to clean")
group.add_argument("-s", "--spaces", action='store_true', help="Clean space characters such as \\t, \\n")
args = parser.parse_args()
inputfile = args.input
if  inputfile.find(".") == -1:
    sys.exit(t.colored("File without format is given. Re-run this script with file formats csv/tsv/json","red"))

# Open file

try:
    if inputfile.find(".json") != -1:
        filejson = open(inputfile,"r+")
        data = json.load(filejson)
        column = data[args.column].items()
    elif inputfile.find(".csv") != -1:
        data = pd.read_csv(inputfile)
        column = data[args.column].tolist()
    elif inputfile.find(".tsv") != -1:
        data = pd.read_csv(inputfile, sep='\t')
        column = data[args.column].tolist()
except FileNotFoundError:
    sys.exit(t.colored("File name " + inputfile + " not found !","red"))  

# Clean

clean, variable = {}, {}
count, removed = 0, 0
if args.spaces is True:
    for index in column: 
        clean[count] = index.replace('\t', ' ').replace('\n', ' ')
        count += 1
    data[args.column] = pd.Series(clean)
else:
    for index in column: 
        if index[1][args.variable] not in variable.values():
            clean[count] = index[1]
            variable[count] = index[1][args.variable]
            count += 1
        else:
            removed += 1
    data[args.column] = clean

if inputfile.find(".json") != -1:
    filejson.truncate(0)
    filejson.seek(0)
    json.dump(data, filejson, indent=4)
elif inputfile.find(".csv") != -1:
    data.to_csv(inputfile, index=False)
elif inputfile.find(".tsv") != -1:
    data.to_csv(inputfile, index=False, sep='\t')

if args.spaces is True:
    print(t.colored("Removed space characters !","green"))
else:
    print(t.colored("Removed "+str(removed)+" data","green")) 