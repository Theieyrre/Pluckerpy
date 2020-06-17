import argparse, json, os, sys
import termcolor as t

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Concatenate multiple account json files', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython concat.py account1.json account2.json account3.json\n"
    )
parser.add_argument("jsons", metavar="jsons", nargs="*", help="Names of json files seperated with space")
parser.add_argument("-o", "--output", metavar="output", nargs="?", help="Output file name to concat all, default output.json", default="output.json")
args = parser.parse_args()
files = []
followers = []

# Translate to json

for file in args.jsons:
    if  file.find(".json") == -1:
        if file.find("."):
            file = file.split(".")[0] + ".json"
            print(t.colored("Non json file given as output format. Changing to " + file, "yellow"))
        else:
            file = file + ".json"
    files.append(file)

# Get output filename

if  args.output.find(".json") == -1:
    if args.output.find("."):
        outputname = args.output.split(".")[0] + ".json"
        print(t.colored("Non json file given as output format. Changing to " + outputname, "yellow"))
    else:
        outputname = args.output + ".json"
output = open(outputname, "w")

# Create data to concat jsons

data = {"filenames": [i.split(".")[0] for i in files]}

# Read and concat files

for filename in files:
    if not os.path.isfile(filename):
        sys.exit(t.colored(filename + " is not a file ! ", "red"))
    else:
        with open(filename, "r") as file:
            datajson = json.load(file)
            for follower in datajson["followers"].values():
                followers.append(follower)
data["followers"] = followers
json.dump(data, output, indent=4)


