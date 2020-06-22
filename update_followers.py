import sys, time
import argparse
from decimal import Decimal
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException

import termcolor as t

from colorama import init
init()

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Get followers of a Twitter user', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython followers.py pluckerpy password123 github 1000\n"
    )
parser.add_argument("input", metavar="input", help="[REQUIRED] Topic word, to seach in twitter, to search more than one word add quotes around string")
parser.add_argument("output", metavar="output", nargs="?", help="Output file name to write tsv, default name followers.json", default="followers.json")
parser.add_argument("-b", "--browser", action='store_true', help="Option to open Chrome window to view tweets")
parser.add_argument("-t", "--threshold", metavar="threshold", nargs="?", help="Threshold to write to output file default 100", default=100)
parser.add_argument("-c", "--click", action='store_true', help="Option to open follower on new tab to get location")
parser.add_argument("-w", "--waitlong", action='store_true', help="Option to wait more than 10 seconds on loading elements. Will reduce runtime significantly ! Use only have slow connection")
args = parser.parse_args()

out_put = args.output
in_put = args.input

if  out_put.find(".json") == -1:
    if out_put.find("."):
        out_put = out_put.split(".")[0] + ".json"
        print(t.colored("Non json file given as output format. Changing to " + out_put, "yellow"))
    else:
        out_put = out_put + ".json"

print("Loading json file...", end = "\r")  
if  in_put.find(".json") == -1:
    if in_put.find("."):
        in_put = in_put.split(".")[0] + ".json"
        print(t.colored("Non json file given as load format. Looking for " + in_put, "yellow"))
    else:
        in_put = in_put + ".json"
try:
    outputfile = open(out_put, "w")
    inputfile = open(in_put, "r")
    datajson = json.load(inputfile)
    followers_json = datajson["followers"]
    followers = [i for i in followers_json.values()]
    print("Loading json file..." + t.colored("Done", "green"))
except FileNotFoundError:
    sys.exit(t.colored("File not found to load !", "red"))

# Web Driver Options

options = webdriver.ChromeOptions()
options.binary_location = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
if args.browser is not True:
    options.add_argument('--headless')
options.add_argument("--lang=en")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

sleep = 2.5 if args.waitlong is True else 1

class Twitter:
    def __init__(self, followers):
        self.followers = followers

    def create_browser(self):
        print("Starting Chrome Web Driver...", end = "\r")
        driver = webdriver.Chrome(executable_path=r'chromedriver.exe', options=options)
        print("Starting Chrome Web Driver..." + t.colored("Done", "green"))
        wait = WebDriverWait(driver, 25) if args.waitlong is True else WebDriverWait(driver, 10)
        return driver, wait

    def get_profiles(self):
        count, threshold = 0, 0
        driver, wait = self.create_browser()
        for follower in self.followers:
            percent = Decimal((count / len(self.followers)) * 100)
            print("Gathering Followers " + t.colored(str(round(percent,2)) + "%","magenta"), end="\r")
            link, location, register, following, followers = self.get_location(follower["name"], driver, wait)
            if location == "-":
                self.followers.pop(count)
                continue
            follower["link"] = link
            follower["location"] = location
            follower["register"] = register
            follower["following"] = following
            follower["followers"] = followers
            self.followers[count] = follower
            count += 1
            threshold += 1
            if threshold > int(args.threshold):
                print(t.colored("Saving data to json file ","yellow"), end="\r")
                outputfile.seek(0)
                json.dump(self.followers, outputfile, indent=4)  
                threshold = 0
        outputfile.seek(0)
        json.dump(self.followers, outputfile, indent=4) 

    def get_location(self, name, driver, wait):
        url = "https://twitter.com/" + name
        driver.execute_script("window.open('{}');".format(url))
        window_after = driver.window_handles[1]
        window_before = driver.window_handles[0]
        driver.switch_to.window(window_after)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='primaryColumn']")))
        column = driver.find_element_by_css_selector("div[data-testid='primaryColumn']")
        wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='UserProfileHeader_Items']")))
        info_div = column.find_element_by_css_selector("div[data-testid='UserProfileHeader_Items']")
        try:
            link = info_div.find_element_by_css_selector("a").get_attribute("href")
        except NoSuchElementException:
            link = "-"

        spans = info_div.find_elements_by_css_selector("span:not([dir])")
        try:
            location = spans[2].get_attribute("innerHTML")
        except IndexError:
            location = "-"

        register = spans[-1].get_attribute("innerHTML").split("</svg>")[1].split("Joined ")[1]

        div_titled = column.find_elements_by_css_selector("a[title]")
        if len(div_titled) < 2:
            div_titled = column.find_elements_by_css_selector("div[title]")            
        following = div_titled[0].find_element_by_css_selector("span").find_element_by_css_selector("span").get_attribute("innerHTML")

        followers = div_titled[1].find_element_by_css_selector("span").find_element_by_css_selector("span").get_attribute("innerHTML")
        driver.close()
        driver.switch_to.window(window_before)
        return link, location, register, following, followers


# Create Twitter Object

twitter = Twitter(followers)
twitter.get_profiles()


