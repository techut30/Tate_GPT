import os
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dateutil.parser import parse

# Twitter login credentials (replace with your own)
TWITTER_USERNAME = "Avg_Engineer7"
TWITTER_PASSWORD = "Iamthebest.30"

# Target Twitter handle to scrape
TARGET_HANDLE = "Cobratate"

# Directory to save tweets
RAW_DIR = "/Users/uttakarsh/Desktop/GPT Tate/data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

def sanitize_filename(text, length=30):
    text = re.sub(r"[\\/:*?\"<>|]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text[:length].strip("_")

def login_twitter(driver):
    driver.get("https://twitter.com/i/flow/login")
    wait = WebDriverWait(driver, 30)

    # Enter username
    username_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
    username_input.send_keys(TWITTER_USERNAME)
    username_input.send_keys(Keys.RETURN)
    time.sleep(2)

    # Enter password
    password_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
    password_input.send_keys(TWITTER_PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for login to complete

def scroll_and_collect_tweets(driver, max_tweets=200):
    driver.get(f"https://twitter.com/{TARGET_HANDLE}")
    time.sleep(5)

    tweets_collected = set()
    tweets_data = []

    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempt = 0

    while len(tweets_collected) < max_tweets and scroll_attempt < 10:
        tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

        for tweet in tweets:
            try:
                tweet_text = tweet.find_element(By.CSS_SELECTOR, 'div[lang]').text
            except:
                tweet_text = ""
            try:
                timestamp = tweet.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                tweet_date = parse(timestamp).date().isoformat()
            except:
                tweet_date = ""

            if tweet_text and (tweet_text, tweet_date) not in tweets_collected:
                tweets_collected.add((tweet_text, tweet_date))
                tweets_data.append({"text": tweet_text, "date": tweet_date})

        # Scroll down
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(5)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempt += 1
        else:
            scroll_attempt = 0
            last_height = new_height

    return tweets_data

def save_tweets(tweets):
    for tweet in tweets:
        snippet = sanitize_filename(tweet["text"])
        filename = f"tweet_{tweet['date']}_{snippet}.txt"
        out_path = os.path.join(RAW_DIR, filename)
        if not os.path.exists(out_path):
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(tweet["text"])
            print(f"Saved: {filename}")

def main():
    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment to run without opening browser window

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        login_twitter(driver)
        tweets = scroll_and_collect_tweets(driver, max_tweets=200)
        save_tweets(tweets)
        print(f"Total tweets saved: {len(tweets)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
