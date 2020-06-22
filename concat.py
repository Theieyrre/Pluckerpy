import argparse, json, os, sys, random
import termcolor as t

from colorama import init
init()

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Concatenate multiple account json files', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython concat.py account1.json account2.json account3.json\n"
    )
parser.add_argument("dir", metavar="dir", help="Names of json files seperated with space")
parser.add_argument("-o", "--output", metavar="output", nargs="?", help="Output file name to concat all, default output.json", default="output.json")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose for extra prints")
args = parser.parse_args()
files = os.listdir(args.dir)
print(args)
if args.verbose is True:
    print("List of all files inside directory: " + t.colored(args.dir))
    print(files)
followers = []

# Get output filename
output = args.output
if  output.find(".json") == -1:
    if output.find("."):
        output = output.split(".")[0] + ".json"
        print(t.colored("Non json file given as output format. Changing to " + output, "yellow"))
    else:
        output = output + ".json"

# Create data to concat jsons

data = {}

# Priority json names

priority = ['TamimBinHamad', 'dohanews', 'covid19qatar', 'QatarUniversity', 'qatarliving', 'QF', 'qcharity', 'HBKU']
priority = [p+".json" for p in priority]

# Read and concat files

weight, count, total = 330, 0, 0
for filename in files:
    if filename not in priority:
        weight = 330
    else:
        weight = 660
    if not os.path.isfile(args.dir + "/" + filename):
        sys.exit(t.colored(args.dir + "/" + filename + " is not a file ! ", "red"))
    else:
        with open(args.dir + "/" + filename, "r") as file:
            datajson = json.load(file)
            if args.verbose is True:
                print("Filename: " + t.colored(filename, "yellow") + ", Weight: " + t.colored(weight, "yellow") + ", Total: " + t.colored(total, "green"))
            shuffle_list = list(datajson["followers"].values())
            random.shuffle(shuffle_list)
            for follower in shuffle_list:
                followers.append(follower)
                count += 1
                total += 1
                if count == weight:
                    break
    count = 0

# Remove duplicates

unique_followers= []
print("Removing duplicates...", end='\r')
[unique_followers.append(x) for x in followers if x not in unique_followers]
total = len(unique_followers)
print("Removing duplicates..." + t.colored("Done", "green"))

data["followers"] = unique_followers
print(t.colored("Completed!\n") + "Total number of accounts: " + t.colored(total, "green"))
output = open(output, "w")
json.dump(data, output, indent=4)


