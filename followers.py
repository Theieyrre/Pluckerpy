import sys, time
import argparse
from decimal import Decimal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

import pandas as pd
import termcolor as t

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Get followers of a Twitter user', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython app.py tobb 1000 output.csv\n"
    )
parser.add_argument("username", metavar="username", help="[REQUIRED] Username of a valid Twitter Account")
parser.add_argument("password", metavar="password", help="[REQUIRED] Password of a valid Twitter Account")
parser.add_argument("input", metavar="input", help="[REQUIRED] Topic word, to seach in twitter, to search more than one word add quotes around string")
parser.add_argument("min", metavar="min", nargs="?", help="Minimum follower count, default 100", default=100)
parser.add_argument("output", metavar="output", nargs="?", help="Output file name to write tsv, default name output.csv", default="output.csv")
parser.add_argument("-b", "--browser", action='store_true', help="Option to open Chrome window to view tweets")
parser.add_argument("-t", "--threshold", metavar="threshold", nargs="?", help="Threshold to write to output file default 100", default=100)
args = parser.parse_args()

output = args.output
if  output.find(".csv") == -1:
    if output.find("."):
        output = output.split(".")[0] + ".csv"
        print(t.colored("Non csv file given as output format. Changing to " + output, "yellow"))
    else:
        output = output + ".csv"

# Create DataFrame

df = pd.DataFrame(columns = [
    "username", "follower_name"
])

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

url = "https://twitter.com/" + args.input + "/followers"
print("Scraping url  " + t.colored(url, "blue"))
print("Waiting DOM to get ready...", end = "\r")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='primaryColumn']")))
column = driver.find_element_by_css_selector("div[data-testid='primaryColumn']")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "section[role='region']")))
print("Waiting DOM to get ready..." + t.colored("Ready", "green"))

# Scrap Followers

count = 0
last_height = driver.execute_script("return document.body.scrollHeight")
while count <= int(args.min):
    percent = Decimal((count / int(args.min)) * 100)
    print("Gathering Tweets " + t.colored(str(round(percent,1)) + "%","magenta"), end="\r")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    user_cells = column.find_elements_by_css_selector("div[data-testid='UserCell']")
    try:
        for user in user_cells:
            html_a = user.find_element_by_css_selector("a[dir='auto']")
            date = html_a.find_element_by_css_selector("time").get_attribute("datetime")
            name_id = html_a.get_attribute("href").split("/")
            print(name_id.get_attribute("outerHTML"))
            is_verified = False
            try:
                verified = user.find_element_by_css_selector("svg[aria-label='Verified account']")
                is_verified = True
            except NoSuchElementException:
                pass
            count += 1
            if new_height == last_height:
                break
            last_height = new_height
    except StaleElementReferenceException:
        print(t.colored("Page Structure changed !", "red"))