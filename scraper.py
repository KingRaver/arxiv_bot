from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

class TweetScraper:
   def __init__(self):
       options = webdriver.ChromeOptions()
       options.add_argument('--start-maximized')
       options.add_experimental_option('excludeSwitches', ['enable-automation'])
       options.add_argument('--disable-blink-features=AutomationControlled')
       self.driver = webdriver.Chrome(options=options)
       self.wait = WebDriverWait(self.driver, 20)
       self.is_logged_in = False
       self.phone = "YOUR_PHONE_NUMBER_HERE"

   def login_twitter(self, username: str, password: str):
       try:
           logging.info("Starting login process")
           self.driver.get('https://twitter.com/i/flow/login')
           time.sleep(8)
           
           logging.info("Entering username")
           username_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "text")))
           username_input.clear()
           username_input.send_keys(username)
           username_input.send_keys(Keys.RETURN)
           time.sleep(5)
           
           logging.info("Entering password")
           password_input = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
           password_input.send_keys(password)
           password_input.send_keys(Keys.RETURN)
           time.sleep(8)

           # Handle password save popup
           try:
               close_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close"]')))
               self.driver.execute_script("arguments[0].click();", close_button)
               time.sleep(1)
           except:
               logging.info("No password save popup found")

           if self._check_security_prompt():
               logging.info("Handling security check")
               self._handle_security()

           logging.info("Login complete")
           self.is_logged_in = True
           return True
       except Exception as e:
           logging.error(f"Login failed: {e}")
           return False

   def _check_security_prompt(self):
       try:
           security_elements = self.driver.find_elements(By.CSS_SELECTOR, 'input[name="text"]')
           return len(security_elements) > 0
       except:
           return False

   def _handle_security(self):
       try:
           phone_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="text"]')))
           phone_input.send_keys(self.phone)
           phone_input.send_keys(Keys.RETURN)
           time.sleep(5)
           
           code = input("Enter verification code from SMS: ")
           code_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="text"]')))
           code_input.send_keys(code)
           code_input.send_keys(Keys.RETURN)
           time.sleep(5)
       except Exception as e:
           logging.error(f"Security verification failed: {e}")

   def post_tweet(self, text):
       if not self.is_logged_in:
           logging.error("Must be logged in to tweet")
           return False
       try:
           self.driver.get('https://twitter.com/compose/tweet')
           time.sleep(5)
           
           # Enter tweet text
           tweet_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]')))
           tweet_input.clear()
           tweet_input.send_keys(text)
           time.sleep(2)
           
           # Find and click post button
           post_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]')))
           self.driver.execute_script("arguments[0].click();", post_button)
           time.sleep(5)
           
           # Handle popup
           try:
               got_it_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Got it']")))
               self.driver.execute_script("arguments[0].click();", got_it_button)
               time.sleep(1)
           except:
               logging.info("No popup found or already closed")
           
           return True
       except Exception as e:
           logging.error(f"Tweet failed: {e}")
           return False

   def close(self):
       self.driver.quit()
