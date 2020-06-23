import sys, time, argparse, json, re
from decimal import Decimal


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

import termcolor as t

from colorama import init
init()

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Get profile and tweets of a Twitter user', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython profile.py pluckerpy password123 github 1000\n"
    )
parser.add_argument("username", metavar="username", help="[REQUIRED] Username of a valid Twitter Account")
parser.add_argument("password", metavar="password", help="[REQUIRED] Password of a valid Twitter Account")
parser.add_argument("input", metavar="input", help="[REQUIRED] @name of a profile page")
parser.add_argument("min", metavar="min", nargs="?", help="Minimum tweet count, default 100", default=100)
parser.add_argument("output", metavar="output", nargs="?", help="Output file name to write tsv, default name output.csv", default="profile.json")
parser.add_argument("-b", "--browser", action='store_true', help="Option to open Chrome window to view tweets")
parser.add_argument("-t", "--threshold", metavar="threshold", nargs="?", help="Threshold to write to output file default 100", default=100)
parser.add_argument("-c", "--click", action='store_true', help="Option to open tweet on new tab to get location")
parser.add_argument("-w", "--waitlong", action='store_true', help="Option to wait more than 10 seconds on loading elements. Will reduce runtime significantly ! Use only have slow connection")
args = parser.parse_args()

output = args.output
if  output.find(".json") == -1:
    if output.find("."):
        output = output.split(".")[0] + ".json"
        print(t.colored("Non json file given as output format. Changing to " + output, "yellow"))
    else:
        output = output + ".json"
output = open(output, "w")

# Create Dictionary

data = {}

# Web Driver Options

print("Creating Chrome Web Driver...", end = "\r")
options = webdriver.ChromeOptions()
options.binary_location = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
if args.browser is not True:
    options.add_argument('--headless')
options.add_argument("--lang=en")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
print("Creating Chrome Web Driver..." + t.colored("Done", "green"))

# Start Chrome WebDriver

print("Starting Chrome Web Driver...", end = "\r")
driver = webdriver.Chrome(executable_path=r'chromedriver.exe', options=options)
print("Starting Chrome Web Driver..." + t.colored("Done", "green"))
url = "https://twitter.com/login"
print("Waiting page to open...", end = "\r")
driver.get(url)
wait = WebDriverWait(driver, 25) if args.waitlong is True else WebDriverWait(driver, 10)
print("Waiting page to open..." + t.colored("Done", "green"))
print("Entering credentials...", end="\r")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "input[name='session[username_or_email]']")))
username_area = driver.find_element_by_css_selector("input[name='session[username_or_email]']")
password_area = driver.find_element_by_css_selector("input[name='session[password]']")
username_area.send_keys(args.username)
password_area.send_keys(args.password)
driver.find_element_by_css_selector("div[data-testid='LoginForm_Login_Button']").click()
if driver.current_url.find("error") != -1:
    driver.close()
    sys.exit(t.colored("Wrong Username/Password !", "red"))
else:
    print(t.colored(" * Login successful ! * ", "green"), end="\r")
url = "https://twitter.com/" + args.input + "/with_replies"
print("Waiting page to open...", end = "\r")
driver.get(url)
wait = WebDriverWait(driver, 10)
print("Waiting page to open..." + t.colored("Done", "green"))
print("Scraping url  " + t.colored(url, "blue"))
print("Waiting DOM to get ready...", end = "\r")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='primaryColumn']")))
column = driver.find_element_by_css_selector("div[data-testid='primaryColumn']")
try:
    wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[aria-label*='Timeline']")))
    try_again = column.find_element_by_css_selector("div[aria-label*='Timeline']")
except NoSuchElementException:
    pass
    #driver.close()
    #sys.exit(t.colored("No user or locked account with name "+args.input+" !", "red"))
wait.until(presence_of_element_located((By.CSS_SELECTOR, "h2[aria-level='2']")))
print("Waiting DOM to get ready..." + t.colored("Ready", "green"))

# Scrap profile data

time.sleep(2)
header = column.find_element_by_css_selector("h2[aria-level='2']")
profile = header.find_element_by_xpath("..")
name_div = header.find_elements_by_css_selector("div")[2]
main_name = "-"
name_emojis = ""
for span in name_div.find_elements_by_css_selector("span"):
    if span.get_attribute("dir") == "auto":
        emoji_div = span.find_element_by_css_selector("div")
        name_emojis += emoji_div.find_element_by_css_selector("img").get_attribute("src") + ","
    else:
        inside = span.get_attribute("innerHTML")
        if inside != " " and len(inside) != 0:
            main_name = inside
if len(name_emojis) == 0:
    name_emojis = "-"
total_tweets = profile.find_element_by_css_selector("div[dir='auto']").get_attribute("innerHTML").split(" ")[0]
try:
    bio_div = column.find_element_by_css_selector("div[data-testid='UserDescription']")
    bio = ""
    bio_emojis = ""
    for span in bio_div.find_elements_by_css_selector("span"):
        if span.get_attribute("dir") == "auto":
            emoji_div = span.find_element_by_css_selector("div")
            bio_emojis += emoji_div.find_element_by_css_selector("img").get_attribute("src") + ","
        else:
            bio += span.get_attribute("innerHTML")
    if len(bio_emojis) == 0:
        bio_emojis = "-"
except NoSuchElementException:
    bio = "-"
    bio_emojis = "-"
data['screen_name'] = main_name
data['name_emojis'] = name_emojis
data['name'] = args.input
data['bio'] = bio
data['bio_emojis'] = bio_emojis
data['total_tweets'] = total_tweets

is_verified = False
try:
    verified = profile.find_element_by_css_selector("svg[aria-label='Verified account']")
    is_verified = True
except NoSuchElementException:
    pass
data['is_verified'] = is_verified

info_div = column.find_element_by_css_selector("div[data-testid='UserProfileHeader_Items']")
try:
    link = info_div.find_element_by_css_selector("a").get_attribute("href")
except NoSuchElementException:
    link = "-"
data['link'] = link

spans = info_div.find_elements_by_css_selector("span:not([dir])")
try:
    location = spans[2].get_attribute("innerHTML")
except IndexError:
    location = "-"
data['location'] = location

register = spans[-1].get_attribute("innerHTML").split("</svg>")[1].split("Joined ")[1]
data['register'] = register

following = column.find_element_by_css_selector("a[href='/"+ args.input +"/following']").find_element_by_css_selector("span").find_element_by_css_selector("span").get_attribute("innerHTML")
data['following'] = following

followers = column.find_element_by_css_selector("a[href='/"+ args.input +"/followers']").find_element_by_css_selector("span").find_element_by_css_selector("span").get_attribute("innerHTML")
data['followers'] = followers

# Scrap Tweets

count,  threshold = 0 , 0
tweets = {}
variable = {}
last_height = driver.execute_script("return document.body.scrollHeight")
if int(args.min) == -1:
    letter = total_tweets[-1]
    if letter == "K":
        max = float(total_tweets[:-1]) * 1000 + 100
    elif letter == "M":
        max = float(total_tweets[:-1]) * 1000000 + 10000
    else:
        max = int(total_tweets)
else:
    max = int(args.min)
while count <= max:
    percent = Decimal((count / max) * 100)
    print("Gathering Tweets  " + t.colored(str(round(percent,1)) + "%","magenta"), end="\r")
    wait.until(presence_of_element_located((By.CSS_SELECTOR, "article")))
    articles = column.find_elements_by_css_selector("article")
    if len(articles) == 0:
        print(t.colored("No tweets found !", "red"))
        break
    try:
        for article in articles:
            try:
                tweet = article.find_element_by_css_selector("div[data-testid='tweet']")
                try:
                    html_a = tweet.find_element_by_css_selector("a[dir='auto']")
                except NoSuchElementException:
                    threshold += 1
                    count += 1
                    if threshold > int(args.threshold):
                        print(t.colored("Saving data to CSV file","yellow"), end="\r")
                        output.seek(0)
                        json.dump(data, output, indent=4) 
                    continue
                date = html_a.find_element_by_css_selector("time").get_attribute("datetime")
                name_id = html_a.get_attribute("href").split("/")
                name = name_id[-3]
                tweet_id = name_id[-1]
                replies = 0
                retweets = 0
                likes = 0
                try:
                    replies_list = tweet.find_element_by_css_selector("div[data-testid='reply']").get_attribute("aria-label").split(" ")
                    if len(replies_list) != 1:
                        replies = replies_list[0]
                except NoSuchElementException:
                    pass
                try:
                    retweets_list = tweet.find_element_by_css_selector("div[data-testid='retweet']").get_attribute("aria-label").split(" ")
                    if len(retweets_list) != 1:
                        retweets = retweets_list[0]
                except NoSuchElementException:
                    pass
                try:
                    likes_list = tweet.find_element_by_css_selector("div[data-testid='like']").get_attribute("aria-label").split(" ")
                    if len(likes_list) != 1:
                        likes = likes_list[0]
                except NoSuchElementException:
                    pass
                            
                retweet_name = "-"
                try:
                    retweet = article.find_element_by_css_selector("span[dir='ltr']")
                    temp = name
                    name = args.input
                    retweet_name = temp
                    is_retweet = True
                except NoSuchElementException:
                    is_retweet = False

                try:
                    content = tweet.find_element_by_css_selector("div[lang]")
                    spans = content.find_elements_by_css_selector("span")
                    tweet_content = ""
                    tweet_emojis = ""
                    for span in spans:
                        if span.get_attribute("aria-hidden") == "true":
                            continue
                        if span.get_attribute("dir") == "auto":
                            emoji_div = span.find_element_by_css_selector("div")
                            tweet_emojis += emoji_div.find_element_by_css_selector("img").get_attribute("src") + ","
                        tweet_content += span.text
                    if len(tweet_emojis) == 0:
                        tweet_emojis = "-"
                    lang = content.get_attribute("lang")
                    mentions = ""
                    try:
                        mentions_list = content.find_elements_by_css_selector("a[href^='/']")
                        mentions = ""
                        for mention in mentions_list:
                            mentions += mention.text
                    except NoSuchElementException:
                        pass
                    if len(mentions) == 0:
                        mentions = "-"
                except NoSuchElementException:
                    tweet_content = "-"
                    tweet_emojis = "-"
                    lang = "-"
                    mentions = "-"

                media = "-"
                try:
                    media = tweet.find_element_by_css_selector("video").get_attribute("src")
                except NoSuchElementException:
                    pass
                try:
                    media = tweet.find_element_by_css_selector("img[alt='Image']").get_attribute("src")
                except NoSuchElementException:
                    pass

                quote_name = "-"
                quote = ""
                try:
                    block_content = article.find_element_by_css_selector("div[role='blockquote']")
                    div = block_content.find_element_by_css_selector("div[dir='ltr']")
                    quote_name = div.find_element_by_css_selector("span").text.split("@")[1]
                    quote_content = block_content.find_element_by_css_selector("div[lang]")
                    spans = quote_content.find_elements_by_css_selector("span")
                    for span in spans:
                        if span.get_attribute("aria-hidden") == "true":
                            continue
                        quote += span.text           
                except NoSuchElementException:
                    quote = "-"

                link = ""
                try:
                    urls = tweet.find_elements_by_css_selector("a[href^='http']")
                    for url in urls:
                        link += url.get_attribute("href") + " "
                except NoSuchElementException:
                    pass
                if len(link) == 0:
                    link = "-"

                tweet_link = "/" + name + "/status/" + tweet_id
                tweet_dict = {
                    'id': tweet_id,
                    'name': name,
                    'date': date,
                    'is_retweet': is_retweet,
                    'retweet_name': retweet_name,
                    'tweet': tweet_content,
                    'tweet_emojis': tweet_emojis,
                    'retweets': retweets,
                    'likes': likes,
                    'replies': replies,
                    'tweet_link': tweet_link,
                    'lang': lang,
                    'media': media,
                    'quote_name': quote_name,
                    'quote': quote,
                    'mentions': mentions,
                    'links': link
                }
                if args.click is True:
                    driver.execute_script("window.open('{}');".format(tweet_link))
                    window_after = driver.window_handles[1]
                    window_before = driver.window_handles[0]
                    driver.switch_to.window(window_after)
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "a[href$='/how-to-tweet#source-labels']")))
                    source_element = driver.find_element_by_css_selector("a[href$='/how-to-tweet#source-labels']")
                    source = source_element.find_element_by_css_selector("span").get_attribute("innerHTML")
                    tweet_dict["source"] = source
                    driver.execute_script("window.close();") 
                    driver.switch_to.window(window_before)
                if tweet_dict["id"] not in variable.values():
                    tweets[count] = tweet_dict
                    data["tweets"] = tweets
                    variable[count] = tweet_dict["id"]
                    count += 1
                    threshold += 1
                if threshold > int(args.threshold):
                    print(t.colored("Saving data to CSV file","yellow"), end="\r")
                    output.seek(0)
                    json.dump(data, output, indent=4)
                if count >= max:
                    break  
            except StaleElementReferenceException:
                print(t.colored("Page Structure changed !", "red"))
                articles = column.find_elements_by_css_selector("article")
                continue
    except TimeoutException:
        print(t.colored("Twitter rate limit reached !", "red"))
        if tweet_dict["id"] not in variable.values():
            tweets[count] = tweet_dict
            data["tweets"] = tweets
        output.seek(0)
        json.dump(data, output, indent=4)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    last_height = new_height
output.seek(0)
print("Completed! Total number of tweets: " + str(count))
json.dump(data, output, indent=4) 
driver.close()