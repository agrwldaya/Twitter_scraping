#!/usr/bin/env python
 

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import requests
import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def wait_and_find_element(driver, by, value, timeout=20, raise_exception=True):
    """Utility function to wait for and find an element"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        if raise_exception:
            raise
        return None

def setup_driver():
    """Setup and return configured Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service("C:/Users/user/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver

def login_to_twitter(driver):
    """Handle Twitter login process with flexible email verification"""
    try:
        # Open Twitter login page
        driver.get("https://twitter.com/i/flow/login")
        print("Opened login page")
        time.sleep(5)

        # Enter username
        username_selectors = [
            "//input[@autocomplete='username']",
            "//input[@name='text']",
            "//input[@autocomplete='username'][not(@type='hidden')]",
            "//input[contains(@class, 'r-30o5oe')]"
        ]

        username_input = None
        for selector in username_selectors:
            username_input = wait_and_find_element(driver, By.XPATH, selector, timeout=5, raise_exception=False)
            if username_input:
                print(f"Found username field")
                break

        if not username_input:
            raise Exception("Could not find username input field")

        # Enter username slowly
        username_input.clear()
        time.sleep(1)
        username = os.getenv('TWITTER_USERNAME')
        for char in username:
            username_input.send_keys(char)
            time.sleep(0.1)
        time.sleep(1)
        username_input.send_keys(Keys.RETURN)
        print("Entered username")
        time.sleep(3)

        # Check for email verification
        # Check for email verification
        email_input = wait_and_find_element(
            driver, 
            By.XPATH, 
            "//input[@autocomplete='text']", 
            timeout=5,
            raise_exception=False
        )

        if email_input:
            print("Email verification required")
            email_input.clear()
            time.sleep(1)
            email = os.getenv('TWITTER_EMAIL')
            for char in email:
                email_input.send_keys(char)
                time.sleep(0.1)
            time.sleep(1)
            email_input.send_keys(Keys.RETURN)
            print("Entered email")
            time.sleep(5)  # Increased sleep to give more time
        else:
            print("No email verification required")


        # Enter password
        password_input = wait_and_find_element(
            driver,
            By.XPATH,
            "//input[@name='password']"
        )
        password_input.clear()
        time.sleep(1)
        password = os.getenv('TWITTER_PASSWORD')
        for char in password:
            password_input.send_keys(char)
            time.sleep(0.1)
        time.sleep(1)
        password_input.send_keys(Keys.RETURN)
        print("Entered password")

        # Wait for login to complete
        time.sleep(5)

        # Verify login success
        if "home" in driver.current_url:
            print("Login successful!")
            return True
        else:
            print("Login verification needed. Current URL:", driver.current_url)
            return False

    except Exception as e:
        print(f"Login failed: {str(e)}")
        driver.save_screenshot("login_error.png")
        raise e

def get_trending_topics(driver):
    """Extract trending topics from Twitter"""
    try:
        print("Waiting for trending topics to load...")
        time.sleep(10)

        trending_selectors = [
            '//div[contains(@aria-label, "Timeline: Trending now")]'
        ]

        trending_section = None
        for selector in trending_selectors:
            trending_section = wait_and_find_element(driver, By.XPATH, selector, timeout=5, raise_exception=False)
            if trending_section:
                print("Found trending section")
                break

        if not trending_section:
            raise Exception("Could not find trending section")

        # Collect the first trending post
        first_trend = trending_section.find_element(By.XPATH, './/div[@role="link"]')
        trends_list = []
        if first_trend:
            first_trend_text = first_trend.text.strip()
            if first_trend_text:
                print(f"1. {first_trend_text}")
                trends_list.append(first_trend_text)

        # Collect subsequent trending posts
        trends = trending_section.find_elements(By.XPATH, './/div[@data-testid="trend"]')
        for i, trend in enumerate(trends, start=2):
            try:
                trend_text = trend.text.strip()
                if trend_text:
                    print(f"{i}. {trend_text}")
                    trends_list.append(trend_text)
                if len(trends_list) >= 5:
                    break  # Stop after collecting top 5 trends
            except Exception as e:
                print(f"Error processing trend {i}: {str(e)}")

        if len(trends_list) < 5:
            print(f"Only found {len(trends_list)} trends, please check manually.")
        
        return trends_list

    except Exception as e:
        print(f"Error getting trending topics: {str(e)}")
        driver.save_screenshot("trending_error.png")
        raise e


def store_in_mongodb(trends):
    """Store trending topics in MongoDB"""
    try:
        client = pymongo.MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        db = client["twitter_data"]
        collection = db["trending_topics"]

        document = {
            "trends": trends,
            "date_time": datetime.now(),
            "ip_address": requests.get("https://api.ipify.org").text
        }

        result = collection.insert_one(document)
        print("Data stored in MongoDB with unique ID:", result.inserted_id)

    except Exception as e:
        print(f"MongoDB storage error: {str(e)}")
        raise e

def main():
    driver = None
    try:
        driver = setup_driver()
        if login_to_twitter(driver):
            trends = get_trending_topics(driver)
            if trends:
                store_in_mongodb(trends)
    
    except Exception as e:
        print(f"Main execution error: {str(e)}")
        if driver:
            driver.save_screenshot("main_error.png")
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()