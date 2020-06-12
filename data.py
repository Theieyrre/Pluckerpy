import json, sys, argparse
import termcolor as t

parser = argparse.ArgumentParser(
    description='Label followers or update labeled json, default write', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython data.py -w\n"
    )
group = parser.add_mutually_exclusive_group()
group.add_argument("-w", "--write", action='store_true', help="Create JSON file and write it")
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
        print(t.colored("Non csv file given as output format. Changing to " + filename, "yellow"))
    else:
        filename = filename.split(".")[0] + ".json"
        print(t.colored("Non csv file given as output format. Changing to " + filename, "yellow"))

account = {}

main_name, name = "", ""
tr_index, amb_index = 0, 0
tr_dict, amb_dict = {}, {}
if args.write is True:
    main_name = input("Enter account screen name: ")
    name = input("Enter account name: ")
elif args.update is True:
    try:
        filejson = open(filename,"r")
    except FileNotFoundError:
        sys.exit(t.colored("File not found to update !", "red"))
    data = json.load(filejson)
    tr_dict = data["tr_followers"]
    tr_index = len(tr_dict)
    amb_dict = data["amb_followers"]
    amb_index = len(amb_dict)
    main_name = data["screen_name"]
    name = data["name"]

account["screen_name"] = main_name
account["name"] = name
while True:
    follower = {}
    try:
        f_main_name = input("Enter follower screen name: ")
        follower["screen_name"] = f_main_name
        f_name = input("Enter account name: ")
        follower["name"] = f_name
        f_label = input("Enter label: ")
        follower["label"] = f_label
        f_list = input("Enter list name:(T/A) ")
        if f_list.lower() == "t":
            tr_dict[tr_index] = follower
            tr_index += 1
        elif f_list.lower() == "a":
            amb_dict[amb_index] = follower
            amb_index += 1
    except KeyboardInterrupt:
        print(t.colored("Followers complete !", "yellow"))
        account["tr_followers"] = tr_dict
        account["amb_followers"] = amb_dict
        break

if len(filename) != 0:
    file = open(filename, "w")
else:
    file = open("./labeled/"+name+".json", "w")
    filename = name+".json"
file.seek(0)
json.dump(account, file, indent=4)
sys.exit(t.colored("Data saved in "+filename, "green"))

