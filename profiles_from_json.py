import json, argparse, os
import tqdm

parser = argparse.ArgumentParser(
    description='Get Profiles from concat.py output json', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython profiles_from_json pluckerpy pass123 output.json\n"
    )
parser.add_argument("username", metavar="username", help="[REQUIRED] Username of a valid Twitter Account")
parser.add_argument("password", metavar="password", help="[REQUIRED] Password of a valid Twitter Account")
parser.add_argument("jsonfile", metavar="jsonfile", help="JSON output of concat.py")
args = parser.parse_args()

inputjson = open(args.jsonfile, "r")
followers = json.load(inputjson)["followers"]
for follower in tqdm(followers):
    options = args.username + ' ' + args.password + ' ' + follower["name"] +  ' ' + str(5000) + ' ' + './downloaded/' + follower["name"]
    os.system('python profile.py ' + options)