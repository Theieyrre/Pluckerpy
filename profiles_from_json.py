import json, argparse, os

parser = argparse.ArgumentParser(
    description='Get Profiles from concat.py output json', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython profiles_from_json pluckerpy pass123 output.json\n"
    )
parser.add_argument("username", metavar="username", help="[REQUIRED] Username of a valid Twitter Account")
parser.add_argument("password", metavar="password", help="[REQUIRED] Password of a valid Twitter Account")
parser.add_argument("jsonfile", metavar="jsonfile", help="JSON output of concat.py")
parser.add_argument("directory", metavar="directory", help="Directory name to make and download in")
parser.add_argument("-b", "--browser", action='store_true', help="Option to open Chrome window to view tweets")
args = parser.parse_args()

inputjson = open(args.jsonfile, "r")
try:
    os.mkdir(args.directory)
except FileExistsError:
    pass

followers = json.load(inputjson)["followers"]
for follower in followers:
    options = [
        args.username,
        args.password,
        follower["name"],
        str(5000),
        args.directory + "/" + follower["name"] + ".json"
    ]
    if args.browser is True:
        options.append('-b')
    options = " ".join(options)
    os.system('python profile.py ' + options)