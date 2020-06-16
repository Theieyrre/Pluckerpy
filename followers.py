import sys, time
import argparse
from decimal import Decimal
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

import termcolor as t

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Get followers of a Twitter user', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython followers.py pluckerpy password123 github 1000\n"
    )
parser.add_argument("username", metavar="username", help="[REQUIRED] Username of a valid Twitter Account")
parser.add_argument("password", metavar="password", help="[REQUIRED] Password of a valid Twitter Account")
parser.add_argument("input", metavar="input", help="[REQUIRED] Topic word, to seach in twitter, to search more than one word add quotes around string")
parser.add_argument("min", metavar="min", nargs="?", help="Minimum follower count, default 100", default=100)
parser.add_argument("output", metavar="output", nargs="?", help="Output file name to write tsv, default name output.csv", default="followers.json")
parser.add_argument("-b", "--browser", action='store_true', help="Option to open Chrome window to view tweets")
parser.add_argument("-t", "--threshold", metavar="threshold", nargs="?", help="Threshold to write to output file default 100", default=100)
parser.add_argument("-c", "--click", action='store_true', help="Option to open follower on new tab to get location")
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

data = {'name': args.input}

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
if args.waitlong is True:
    wait = WebDriverWait(driver, 25)
else:
    wait = WebDriverWait(driver, 10)
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

if int(args.min) == -1:
    url = "https://twitter.com/" + args.input
    print("Getting total follower count  " + t.colored(url, "blue"))
    driver.get(url)
    print("Waiting DOM to get ready...", end = "\r")
    wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='primaryColumn']")))
    column = driver.find_element_by_css_selector("div[data-testid='primaryColumn']")
    wait.until(presence_of_element_located((By.CSS_SELECTOR, "a[href='/"+ args.input +"/followers']")))
    followers = column.find_element_by_css_selector("a[href='/"+ args.input +"/followers']").find_element_by_css_selector("span").find_element_by_css_selector("span").get_attribute("innerHTML")
    letter = followers[-1]
    if letter == "K":
        max = float(followers[:-1]) * 1000 + 100
    elif letter == "M":
        max = float(followers[:-1]) * 1000000 + 10000
    else:
        max = int(followers)
else:
    max = int(args.min)

url = "https://twitter.com/" + args.input + "/followers"
driver.get(url)
print("Scraping url  " + t.colored(url, "blue"))
print("Waiting DOM to get ready...", end = "\r")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='primaryColumn']")))
time.sleep(2)
column = driver.find_element_by_css_selector("div[data-testid='primaryColumn']")
try:
    try_again = column.find_element_by_css_selector("div[aria-label='Timeline: Followers']")
except NoSuchElementException:
    driver.close()
    sys.exit(t.colored("No user with name "+args.input+" !", "red"))
# wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Timeline: Followers']")))
print("Waiting DOM to get ready..." + t.colored("Ready", "green"))

# Get Name

screen_name = column.find_element_by_css_selector("h2[aria-level='2']").find_element_by_css_selector("span").get_attribute("innerHTML")
data["screen_name"] = screen_name

# Scrap Followers

count, threshold = 0, 0
last_height = driver.execute_script("return document.body.scrollHeight")
followers = {}
while count <= max:
    percent = Decimal((count / max) * 100)
    print("Gathering Followers " + t.colored(str(round(percent,1)) + "%","magenta"), end="\r")
    try:
        user_cells = column.find_elements_by_css_selector("div[data-testid='UserCell']")
        for user in user_cells:
            main_div = user.find_element_by_css_selector("div.r-16y2uox")
            div_autos = main_div.find_elements_by_css_selector("div[dir='auto']")
            bio = ""
            bio_emojis = ""
            links = ""
            if len(div_autos) == 4:
                bio_div = main_div.find_elements_by_css_selector("div[dir='auto']")[-1]
                for span in bio_div.find_elements_by_css_selector("span"):
                    if span.get_attribute("class") == "r-18u37iz":
                        continue
                    if span.get_attribute("dir") == "auto":
                        emoji_div = span.find_element_by_css_selector("div")
                        bio_emojis += emoji_div.find_element_by_css_selector("img").get_attribute("src") + ","
                    else:
                        bio_text = span.get_attribute("innerHTML")
                        bio += bio_text
                if len(bio_emojis) == 0:
                    bio_emojis = "-"
                try:
                    for a in bio_div.find_elements_by_css_selector("a[href]"):
                        links += a.get_attribute("innerHTML").split("</span>")[-1] + " "
                    if len(links) == 0:
                        links = "-"   
                except NoSuchElementException:
                    links = "-"
            else:
                bio = "-"
                bio_emojis = "-"
                links= "-"             
            name_div = main_div.find_element_by_css_selector("a[href^='/']")
            name = name_div.get_attribute("href").split("/")[-1]
            screen_name = ""
            name_emojis = ""
            for div_auto in name_div.find_elements_by_css_selector("div[dir='auto']"):
                for div in div_auto.find_elements_by_css_selector("div[aria-label]"):
                    name_emojis += div.find_element_by_css_selector("img").get_attribute("src") + ","
            if len(name_emojis) == 0:
                name_emojis = "-"
            for span in user.find_element_by_css_selector("div[dir='auto']").find_element_by_css_selector("span:not([dir])").find_elements_by_css_selector("span:not([dir])"):
                if span.get_attribute("innerHTML") != " ":
                    screen_name += span.get_attribute("innerHTML")
            try:
                verified = user.find_element_by_css_selector("svg[aria-label='Verified account']")
                is_verified = True
            except NoSuchElementException:
                is_verified = False
            try:
                locked = user.find_element_by_css_selector("svg[aria-label='Protected account']")
                is_locked = True
            except NoSuchElementException:
                is_locked = False
            follower = {
                'screen_name': screen_name,
                'name': name,
                'name_emojis': name_emojis,
                'is_verified': is_verified,
                'is_locked': is_locked,
                'bio': bio,
                'bio_emojis': bio_emojis,
                'links': links
            }
            if args.click is True:
                profile_url = "https://twitter.com/" + name
                driver.execute_script("window.open('{}');".format(profile_url))
                window_after = driver.window_handles[1]
                window_before = driver.window_handles[0]
                driver.switch_to.window(window_after)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='UserProfileHeader_Items']")))
                info_div = driver.find_element_by_css_selector("div[data-testid='UserProfileHeader_Items']")
                spans = info_div.find_elements_by_css_selector("span:not([dir])")
                try:
                    location = spans[2].get_attribute("innerHTML")
                except IndexError:
                    location = "-"
                follower["location"] = location
                driver.execute_script("window.close();") 
                driver.switch_to.window(window_before)
            if follower not in followers.values():
                followers[count] = follower
                threshold += 1
                count += 1
            data["followers"] = followers
            if threshold > int(args.threshold):
                print(t.colored("Saving data to CSV file ","yellow"), end="\r")
                output.seek(0)
                json.dump(data, output, indent=4)  
                threshold = 0
            if count >= max:
                break
    except StaleElementReferenceException:
        print(t.colored("Page Structure changed !", "red"))
    except TimeoutException:
        print(t.colored("Twitter rate limit reached !", "red"))
        if follower not in followers.values():
            followers[count] = follower
        output.seek(0)
        json.dump(data, output, indent=4)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
output.seek(0)
print("Completed! Total number of followers: " + str(count))
json.dump(data, output, indent=4) 
driver.close()