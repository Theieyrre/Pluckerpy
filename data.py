import json, sys, argparse
import termcolor as t

from colorama import init
init()

parser = argparse.ArgumentParser(
    description='Label followers or update labeled json, default write', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython data.py -w\n"
    )
group = parser.add_mutually_exclusive_group()
group.add_argument("-w", "--write", action='store_true', help="Create JSON file and write it", default=True)
group.add_argument("-u", "--update", action='store_true', help="Update existing labeled JSON file")
parser.add_argument("filename", metavar="filename", nargs="?", help="Output file name to write json, default name <account name>.json", default="")
args = parser.parse_args()

filename = args.filename
if  filename.find(".json") == -1 and len(filename) != 0:
    if filename.find("/") != -1:
        directory_list = filename.split("/")[:-1]
        directory = ""
        for w in directory_list:
            directory += w + "/"
        filename = filename.split("/")[-1]
        filename = directory + filename.split(".")[0] + ".json"
        print(t.colored("Non json file given as output format. Changing to " + filename, "yellow"))
    else:
        filename = filename.split(".")[0] + ".json"
        print(t.colored("Non json file given as output format. Changing to " + filename, "yellow"))

account = {}

main_name, name = "", ""
qatar_index, expat_index, other_index = 0, 0, 0
qatar_dict, expat_dict, other_dict = {}, {}, {}
if args.update is True:
    try:
        filejson = open(filename,"r")
    except FileNotFoundError:
        sys.exit(t.colored("File not found to update !", "red"))
    data = json.load(filejson)
    qatar_dict = data["qatar_followers"]
    qatar_index = len(qatar_dict)
    expat_dict = data["expat_followers"]
    expat_index = len(expat_dict)
    other_dict = data["other_followers"]
    other_index = len(other_dict)
    main_name = data["screen_name"]
    name = data["name"]
else:
    main_name = input("Enter account screen name: ")
    name = input("Enter account name: ")
if len(filename) == 0:
    filename = "./labeled/" + name + ".json"

account["screen_name"] = main_name
account["name"] = name
while True:
    follower = {}
    try:
        f_name = input("Enter follower name: ")
        follower["name"] = f_name
        f_label = input("Enter label: ")
        follower["label"] = f_label
        f_list = input("Enter list name:(0,1,2) ")
        if f_list == '0':
            qatar_dict[qatar_index] = follower
            qatar_index += 1
        elif f_list == '1':
            expat_dict[expat_index] = follower
            expat_index += 1
        elif f_list == '2':
            other_dict[other_index] = follower
            other_index += 1
    except KeyboardInterrupt:
        print(t.colored("Followers complete !", "yellow"))
        account["qatar_followers"] = qatar_dict
        account["expat_followers"] = expat_dict
        account["other_followers"] = other_dict
        break

if len(filename) != 0:
    file = open(filename, "w")
else:
    file = open("./labeled/"+name+".json", "w")
    filename = name+".json"
file.seek(0)
json.dump(account, file, indent=4)
sys.exit(t.colored("Data saved in "+filename, "green"))

