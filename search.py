import sys, time
import argparse
from decimal import Decimal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

import pandas as pd
import termcolor as t

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Get tweets of a topic', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython app.py tobb 1000 output.csv\n"
    )
parser.add_argument("input", metavar="input", help="[REQUIRED] Topic word, to seach in twitter, to search more than one word add quotes around string")
parser.add_argument("min", metavar="min", nargs="?", help="Minimum tweet count, default 100", default=100)
parser.add_argument("output", metavar="output", nargs="?", help="Output file name to write tsv, default name output.csv", default="output.csv")
parser.add_argument("-b", "--browser", action='store_true', help="Option to open Chrome window to view tweets")
parser.add_argument("-t", "--threshold", metavar="threshold", nargs="?", help="Threshold to write to output file default 100", default=100)
parser.add_argument("-c", "--click", metavar="click", nargs="?", help="OPtion to click on tweets to get source label")
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
    "id", "name", "is_verified", "date", "tweet", "likes", 
    "replies", "retweets", "tweet_link", "lang", "media",
    "quote_name", "quote", "mentions", "links"
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
url = "https://twitter.com/search?q=" + args.input + "&src=typed_query"
print("Waiting page to open...", end = "\r")
driver.get(url)
wait = WebDriverWait(driver, 10)
print("Waiting page to open..." + t.colored("Done", "green"))
print("Scraping url  " + t.colored(url, "blue"))
print("Waiting DOM to get ready...", end = "\r")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='primaryColumn']")))
column = driver.find_element_by_css_selector("div[data-testid='primaryColumn']")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "section[role='region']")))
print("Waiting DOM to get ready..." + t.colored("Ready", "green"))

# Scrap Tweets

count,  threshold = 0 , 0
last_height = driver.execute_script("return document.body.scrollHeight")
while count <= int(args.min):
    percent = Decimal((count / int(args.min)) * 100)
    print("Gathering Tweets  " + t.colored(str(round(percent,1)) + "%","magenta"), end="\r")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    articles = column.find_elements_by_css_selector("article")
    if len(articles) == 0:
        print(t.colored("No tweets found !", "red"))
        break
    try:
        for article in articles:
            tweet = article.find_element_by_css_selector("div[data-testid='tweet']")
            html_a = tweet.find_element_by_css_selector("a[dir='auto']")
            date = html_a.find_element_by_css_selector("time").get_attribute("datetime")
            name_id = html_a.get_attribute("href").split("/")
            name = name_id[-3]
            tweet_id = name_id[-1]
            is_verified = False
            try:
                verified = tweet.find_element_by_css_selector("svg[aria-label='Verified account']")
                is_verified = True
            except NoSuchElementException:
                pass
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

            try:
                content = tweet.find_element_by_css_selector("div[lang]")
                spans = content.find_elements_by_css_selector("span")
                tweet_content = ""
                for span in spans:
                    if span.get_attribute("aria-hidden") == "true":
                        continue
                    tweet_content += span.text
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
                    mentions = float("NaN")
            except NoSuchElementException:
                pass

            media = float("NaN")
            try:
                media = tweet.find_element_by_css_selector("video").get_attribute("src")
            except NoSuchElementException:
                pass
            try:
                media = tweet.find_element_by_css_selector("img[alt='Image']").get_attribute("src")
            except NoSuchElementException:
                pass

            quote_name = float("NaN")
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
                quote = float("NaN")

            link = ""
            try:
                urls = tweet.find_elements_by_css_selector("a[href^='http']")
                for url in urls:
                    link += url.get_attribute("href") + " "
            except NoSuchElementException:
                pass
            if len(link) == 0:
                link = float("NaN")

            tweet_link = "/" + name + "/status/" + tweet_id
            tweet_dict = {
                "id": tweet_id,
                "name": name,
                "is_verified": is_verified,
                "date": date,
                "tweet": tweet_content,
                "retweets": retweets,
                "likes": likes,
                "replies": replies,
                "tweet_link": tweet_link,
                "lang": lang,
                "media": media,
                "quote_name": quote_name,
                "quote": quote,
                "mentions": mentions,
                "links": link
            }
            if args.click is not None:
                content.click()
                wait.until(presence_of_element_located((By.CSS_SELECTOR, "a[href$='/how-to-tweet#source-labels']")))
                source_element = driver.find_element_by_css_selector("a[href$='/how-to-tweet#source-labels']")
                source = source_element.find_element_by_css_selector("span").get_attribute("innerHTML")
                tweet_dict["source"] = source
                driver.back()
            df = df.append(tweet_dict, ignore_index = True)
            threshold += 1
            count += 1
            if threshold > int(args.threshold):
                print(t.colored("Saving data to CSV file","yellow"), end="\r")
                df = df.drop_duplicates()
                df.to_csv(output, index=False, na_rep="NaN")  
            if new_height == last_height:
                break
            last_height = new_height
    except StaleElementReferenceException:
        print(t.colored("Page Structure changed !", "red"))
df = df.drop_duplicates()
print("Completed! Total number of tweets: " + str(len(df.index)))
driver.close()
df.to_csv(output, index=False, na_rep="NaN")



