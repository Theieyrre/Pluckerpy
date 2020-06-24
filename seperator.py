import json, argparse, os

parser = argparse.ArgumentParser(
    description='Seperate tweets with specific language for labeling', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython seperator.py ar downloaded 0.9\n"
    )
parser.add_argument("language", metavar="language", help="[REQUIRED] Language abbrevation used by Twitter")
parser.add_argument("directory", metavar="directory", help="[REQUIRED] Directory name of downloaded profiles")
parser.add_argument("ratio", metavar="ratio", help="[REQUIRED] Percentage of language=ar to other languages to decide whether move to arabic folder or not")
args = parser.parse_args()

os.makedirs(args.directory + "/" + args.language, exist_ok=True)
print(os.getcwd())

for file in os.listdir(args.directory):
    filename = args.directory + "/" + file
    if not os.path.isfile(filename):
        continue
    ar_count, total_count = 0, 0
    inputfile = open(filename, 'r')
    tweets = json.load(inputfile)["tweets"]
    for tweet in tweets.values():
        lang = tweet["lang"]
        if lang == args.language:
            ar_count += 1
        total_count += 1
    ratio = ar_count / total_count
    inputfile.close()
    print("Ratio of " + filename + "is: " + str(ratio))
    if  ratio > float(args.ratio):
        os.rename(args.directory + "/"+ file, args.directory + "/" + args.language + "/" + file)