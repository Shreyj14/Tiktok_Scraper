

"""# Import Packages"""

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import staleness_of
import re
import pandas as pd
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import random
import sys
import pandas as pd
from datetime import datetime, timedelta
from pyvirtualdisplay import Display

"""# Initate Brwoser"""

# Your browser initialization code

def initiate_browser():
    # # Path to chromedriver
    # driver_path = '/Users/sj/Downloads/chromedriver_mac64/chromedriver'

    # Initialize Chrome browser
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems.
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    browser = webdriver.Chrome( options=options)
    return browser

"""Start Displays for Chromium"""

# Start the virtual display with size 1366x768 (typical screen resolution)
display = Display(visible=0, size=(1366, 768))
display.start()

"""# Get the Intial Post Links
 Gets Post links, username, captions, hashtags from the www.tiktok.com/tag/fashion

 Gets Likes, Saved and Post Date from each post links
"""

def process_date(text):
    today = datetime.now()

    # Hours ago
    if 'h ago' in text:
        hours = int(text.split('h')[0].strip())
        return (today - timedelta(hours=hours)).strftime('%Y-%m-%d')

    # Days ago
    elif 'd ago' in text:
        days = int(text.split('day')[0].strip())
        return (today - timedelta(days=days)).strftime('%Y-%m-%d')

    # Weeks ago
    elif 'w ago' in text:
        weeks = int(text.split('week')[0].strip())
        return (today - timedelta(weeks=weeks)).strftime('%Y-%m-%d')

    # Date format like 2-27
    elif '-' in text and len(text) <= 5:
        month, day = text.split('-')
        return f"{today.year}-{month}-{day}"

    # Assume it's already a date format
    else:
        return text

def extract_post_data(browser, post_link):
    browser.get(post_link)
    time.sleep(5)  # Allow the post page to load

    try:
        post_date_container = browser.find_element(By.CSS_SELECTOR, '[data-e2e="browser-nickname"]')
        span_value = post_date_container.find_elements(By.TAG_NAME, 'span')[-1]
        date_text = span_value.get_attribute('innerText')
        post_date = process_date(date_text)
    except Exception as e:
        print(f"Error: {e}")
        post_date = None

    try:
        like_count = browser.find_element(By.CSS_SELECTOR, '[data-e2e="like-count"]').text
    except:
        like_count = None

    try:
        saved_count = browser.find_element(By.CSS_SELECTOR, '[data-e2e="undefined-count"]').text
    except:
        saved_count = None


    return {
        "Likes": like_count,
        "Saved": saved_count,
        "Date Posted": post_date,
        "Date Created": datetime.now()
    }

def scroll_to_load(browser, desired_post_count):
    current_post_count = len(browser.find_elements(By.CSS_SELECTOR, '.tiktok-1as5cen-DivWrapper.e1cg0wnj1'))

    max_attempts = 10
    no_change_count = 0

    while current_post_count < desired_post_count and no_change_count < max_attempts:
        old_last_post = browser.find_elements(By.CSS_SELECTOR, '.tiktok-1as5cen-DivWrapper.e1cg0wnj1')[-1]

        # Use Page Down key to scroll
        body = browser.find_element(By.CSS_SELECTOR, 'body')
        body.send_keys(Keys.PAGE_DOWN)

        time.sleep(7)  # Increase sleep time to 7 seconds

        # Check post count
        new_post_count = len(browser.find_elements(By.CSS_SELECTOR, '.tiktok-1as5cen-DivWrapper.e1cg0wnj1'))

        if new_post_count > current_post_count:
            current_post_count = new_post_count
            no_change_count = 0
        else:
            no_change_count += 1

    return current_post_count

browser = initiate_browser()
browser.get('https://www.tiktok.com/tag/fashion')
time.sleep(5)  # Allow initial page load

# Scroll to load 100 posts
scroll_to_load(browser, 100)

# After this, you can then fetch the hrefs as before
a_elements = browser.find_elements(By.CSS_SELECTOR, '.tiktok-1as5cen-DivWrapper.e1cg0wnj1 > a')

# Use list comprehensions to extract hrefs and usernames
hrefs = [a.get_attribute('href') for a in a_elements]
username = [a.text if a.text.strip() else a.get_attribute('alt') for a in a_elements]

captions_div_elements = browser.find_elements(By.CSS_SELECTOR, 'div[data-e2e="challenge-item-desc"]')
captions = [div.get_attribute('aria-label') for div in captions_div_elements]
hashtags = [re.findall(r'(#\w+)', caption) for caption in captions]

# Extract data from each href and store in a list
post_data_list = []
for link in hrefs:
    post_data_list.append(extract_post_data(browser, link))

# Convert list of dictionaries into pandas DataFrame
df = pd.DataFrame(post_data_list)

df['Post URL'] = hrefs
df['Account'] = username
df['Captions'] = captions
df['Hashtags'] = hashtags

new_order = ['Post URL','Account', 'Likes', 'Saved', 'Captions', 'Hashtags', 'Date Posted', 'Date Created']
df_tiktok = df[new_order]
df_tiktok.to_csv('./outputs/tiktok_scraped.csv', index=False)
# Close the browser
browser.close()


# Get Comments for each post

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

sys.path.insert(0, '/usr/lib/chromium-browser/chromedriver')  # Adjusting system PATH for Chromedriver

def human_like_delay(min_seconds=2, max_seconds=5):
    """Generates a random sleep duration within the given range."""
    return random.uniform(min_seconds, max_seconds)

def close_popups(driver, timeout=20):
    """Attempts to close popups in a more human-like manner."""
    try:
        # Click on the verification overlay close button if present
        verification_close_button = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#verify-bar-close'))
        )
        # ActionChains(driver).move_to_element(verification_close_button).click().perform()
        time.sleep(human_like_delay())  # Small delay after clicking
        driver.save_screenshot("ver_click.png")

    except TimeoutException:
        print("Verification captcha close button not found or failed to close.")

    try:
        # Now close other popups if they exist (e.g. login popup)
        close_button = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.tiktok-1ecw34m-DivCloseWrapper.e1gjoq3k6'))
        )
        ActionChains(driver).move_to_element(close_button).click().perform()
        time.sleep(human_like_delay())  # Introduce a random sleep after clicking
        driver.save_screenshot("log_click.png")

    except TimeoutException:
        # If unable to close using the close button, try pressing ESC key
        driver.save_screenshot("log_click.png")
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        print("Login popup not found. Trying to close with ESC key.")
        pass

def get_comments(url, css_selector, max_retries=3):
    """Fetch all available comments from the given webpage."""
    retries = 0
    comments = []

    while retries < max_retries:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        try:
            close_popups(driver)

            # Wait for the comments to be visible
            driver.save_screenshot("com.png")  # Optional: For debugging, captures the screen at this point.
            comment_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
            )

            # Extract text from each comment element and store in a list
            comments = [comment_element.text for comment_element in comment_elements]

            # If we successfully retrieve comments, we can break out of the retry loop
            if comments:
                break

        except TimeoutException:
            print("Attempt {}/{}: Failed to fetch the comments.".format(retries + 1, max_retries))
            # you may also want to introduce a delay here before retrying
            # to behave more like a human and less like a bot being blocked by a website's security
            time.sleep(human_like_delay())

        finally:
            retries += 1  # Increase the retry count whether it was a success or fail
            driver.quit()  # make sure to quit the driver after each attempt

    return comments


# Usage:
#URL= ['https://www.tiktok.com/@crescentshay/video/6884764760387128582','https://www.tiktok.com/@jaadiee/video/7198199504405843205','https://www.tiktok.com/@quentaloup/video/7248033321270136070']
CSS_SELECTOR = 'p[data-e2e="comment-level-1"] > span'
list_comments =[]
for href in hrefs:
  comments_list = get_comments(href, CSS_SELECTOR)
  print(comments_list)
  list_comments.append(comments_list)
  time.sleep(2)

df['Comments'] = list_comments
new_order = ['Post URL','Account', 'Likes', 'Comments', 'Saved', 'Captions', 'Hashtags', 'Date Posted', 'Date Created']
df_tiktok = df[new_order]
df_tiktok.to_csv('./outputs/tiktok_scraped_data.csv', index=False)

