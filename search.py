import sys, time
import argparse
from decimal import Decimal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

import pandas as pd
import termcolor as t

from colorama import init
init()

# Parse Arguments and Print Help

parser = argparse.ArgumentParser(
    description='Get tweets of a topic', 
    formatter_class=argparse.RawTextHelpFormatter, 
    epilog="Example of usage:\npython search.py github 1000\n"
    )
parser.add_argument("input", metavar="input", help="[REQUIRED] Topic word, to seach in twitter, to search more than one word add quotes around string")
parser.add_argument("min", metavar="min", nargs="?", help="Minimum tweet count, default 100", default=100)
parser.add_argument("output", metavar="output", nargs="?", help="Output file name to write tsv, default name output.csv", default="search.csv")
parser.add_argument("-b", "--browser", action='store_true', help="Option to open Chrome window to view tweets")
parser.add_argument("-t", "--threshold", metavar="threshold", nargs="?", help="Threshold to write to output file default 100", default=100)
parser.add_argument("-c", "--click", action='store_true', help="Option to open tweet on new tab to get location")
parser.add_argument("-w", "--waitlong", action='store_true', help="Option to wait more than 10 seconds on loading elements. Will reduce runtime significantly ! Use only have slow connection")
parser.add_argument("-s", "--seperator", action='store_true', help="Seperator for csv file")
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
    "id", "name", "is_verified", "date", "tweet", "tweet_emojis", "likes", 
    "replies", "retweets", "tweet_link", "lang", "media",
    "quote_name", "quote", "quote_emojis", "mentions", "links"
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
if args.waitlong is True:
    wait = WebDriverWait(driver, 25)
else:
    wait = WebDriverWait(driver, 10)
print("Waiting page to open..." + t.colored("Done", "green"))
print("Scraping url  " + t.colored(url, "blue"))
print("Waiting DOM to get ready...", end = "\r")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='primaryColumn']")))
column = driver.find_element_by_css_selector("div[data-testid='primaryColumn']")
wait.until(presence_of_element_located((By.CSS_SELECTOR, "section[role='region']")))
print("Waiting DOM to get ready..." + t.colored("Ready", "green"))

# Scrap Tweets

window_before = driver.window_handles[0]
wait.until(presence_of_element_located((By.CSS_SELECTOR, "article")))
count,  threshold = 0 , 0
last_height = driver.execute_script("return document.body.scrollHeight")
while count <= int(args.min):
    percent = Decimal((count / int(args.min)) * 100)
    print("Gathering Tweets  " + t.colored(str(round(percent,1)) + "%","magenta"), end="\r")
    articles = column.find_elements_by_css_selector("article")
    if len(articles) == 0:
        print(t.colored("No tweets found !", "red"))
        break
    try:
        for article in articles:
            try:
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
                quote_emojis = ""
                try:
                    block_content = article.find_element_by_css_selector("div[role='blockquote']")
                    div = block_content.find_element_by_css_selector("div[dir='ltr']")
                    quote_name = div.find_element_by_css_selector("span").text.split("@")[1]
                    quote_content = block_content.find_element_by_css_selector("div[lang]")
                    spans = quote_content.find_elements_by_css_selector("span")
                    for span in spans:
                        if span.get_attribute("aria-hidden") == "true":
                            continue
                        if span.get_attribute("dir") == "auto":
                            emoji_div = span.find_element_by_css_selector("div")
                            quote_emojis += emoji_div.find_element_by_css_selector("img").get_attribute("src") + ","
                        quote += span.text    
                    if len(quote_emojis) == 0:
                        quote_emojis = "-"       
                except NoSuchElementException:
                    quote = "-"
                    quote_emojis = "-"

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
                    "id": tweet_id,
                    "name": name,
                    "is_verified": is_verified,
                    "date": date,
                    "tweet": tweet_content,
                    "tweet_emojis": tweet_emojis,
                    "retweets": retweets,
                    "likes": likes,
                    "replies": replies,
                    "tweet_link": tweet_link,
                    "lang": lang,
                    "media": media,
                    "quote_name": quote_name,
                    "quote": quote,
                    "quote_emojis": quote_emojis,
                    "mentions": mentions,
                    "links": link
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
                df = df.append(tweet_dict, ignore_index = True)
                threshold += 1
                count += 1
                if threshold > int(args.threshold):
                    print(t.colored("Saving data to CSV file","yellow"), end="\r")
                    df = df.drop_duplicates()
                    if args.seperator is True:
                        df.to_csv(output, index=False, na_rep="-", sep=args.seperator)
                    else:
                        df.to_csv(output, index=False, na_rep="-") 
                    threshold = 0 
            except StaleElementReferenceException:
                print(t.colored("Page Structure changed !", "red"))
                articles = column.find_elements_by_css_selector("article")
                continue
    except TimeoutException:
        print(t.colored("Twitter rate limit reached !", "red"))
        df = df.drop_duplicates()
        if args.seperator is True:
            df.to_csv(output, index=False, na_rep="-", sep=args.seperator)
        else:
            df.to_csv(output, index=False, na_rep="-") 
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    last_height = new_height
df = df.drop_duplicates()
print("Completed! Total number of tweets: " + str(len(df.index)))
driver.close()
if args.seperator is True:
    df.to_csv(output, index=False, na_rep="-", sep=args.seperator)
else:
    df.to_csv(output, index=False, na_rep="-")



