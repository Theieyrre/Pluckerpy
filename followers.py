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
while count <= int(args.min):
    percent = Decimal((count / int(args.min)) * 100)
    print("Gathering Followers " + t.colored(str(round(percent,1)) + "%","magenta"), end="\r")
    user_cells = column.find_elements_by_css_selector("div[data-testid='UserCell']")
    try:
        for user in user_cells:
            main_div = user.find_elements_by_css_selector("div.r-5f2r5o")[1]
            div_autos = main_div.find_elements_by_css_selector("div[dir='auto']")
            bio = ""
            if len(div_autos) == 4:
                bio_div = main_div.find_elements_by_css_selector("div[dir='auto']")[-1]
                for span in bio_div.find_elements_by_css_selector("span"):
                    bio_text = span.get_attribute("innerHTML")
                    if span.get_attribute("class") == "r-18u37iz":
                        bio_text = span.find_element_by_css_selector("a").get_attribute("innerHTML")
                    bio += bio_text   
            else:
                bio = "-"             
            name = main_div.find_element_by_css_selector("a[href^='/']").get_attribute("href").split("/")[-1]
            screen_name = user.find_element_by_css_selector("div[dir='auto']").find_element_by_css_selector("span").find_element_by_css_selector("span").get_attribute("innerHTML")
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
                'is_verified': is_verified,
                'is_locked': is_locked,
                'bio': bio
            }
            followers[count] = follower
            data["followers"] = followers
            threshold += 1
            count += 1
            if threshold > int(args.threshold):
                print(t.colored("Saving data to CSV file ","yellow"), end="\r")
                output.seek(0)
                json.dump(data, output, indent=4)  
            if count > int(args.min):
                break
    except StaleElementReferenceException:
        print(t.colored("Page Structure changed !", "red"))
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