import logging
import time
import traceback
from pythonjsonlogger import jsonlogger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Logger setup (same as stdspellingbee.py)
logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
log_file_handler = logging.FileHandler('automation_logs.json', mode='a')
log_file_handler.setFormatter(json_formatter)
stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
logger = logging.getLogger("StudentStoryGen")
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)
logger.addHandler(stream_handler)

def login(driver, email, password):
    try:
        logger.info("Starting login process.", extra={'activity': 'Login', 'step': 'init'})
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.send_keys(email)
        logger.info("Email entered.", extra={'activity': 'Login', 'step': 'email_entered'})
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(password)
        logger.info("Password entered.", extra={'activity': 'Login', 'step': 'password_entered'})
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        logger.info("Login button clicked.", extra={'activity': 'Login', 'step': 'login_button_clicked'})
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav"))
        )
        logger.info("Successfully logged in.", extra={'activity': 'Login', 'status': 'success'})
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", extra={'activity': 'Login', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def start_story_starter_activity(driver):
    try:
        logger.info("Waiting for Classroom tab to be clickable...", extra={'activity': 'StartActivity', 'step': 'wait_classroom_tab'})
        wait = WebDriverWait(driver, 20)
        # Try to find the Classroom tab by span or anchor
        try:
            classroom_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'Classroom')]"))
            )
        except Exception:
            classroom_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space(text())='Classroom']"))
            )
        logger.info("Classroom tab found, clicking...", extra={'activity': 'StartActivity', 'step': 'classroom_tab_found'})
        driver.execute_script("arguments[0].click();", classroom_tab)
        logger.info("Clicked on Classroom tab.", extra={'activity': 'StartActivity', 'step': 'classroom_tab_clicked'})
        time.sleep(2)
        logger.info("Looking for Pending Activity section...", extra={'activity': 'StartActivity', 'step': 'pending_section'})
        pending_section = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Pending Activities')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(false);", pending_section)
        logger.info("Scrolled to Pending Activities section.", extra={'activity': 'StartActivity', 'step': 'pending_section_scrolled'})
        time.sleep(1)
        logger.info("Looking for Story Starter activity in Pending Activities...", extra={'activity': 'StartActivity', 'step': 'find_story_starter'})
        # Scroll a bit more to ensure visibility
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(1)
        start_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Start Activity') or contains(text(), 'Start')]")
        found = False
        for btn in start_buttons:
            try:
                card = btn.find_element(By.XPATH, "ancestor::div[contains(@class, 'flex')][1]")
                if 'story starter' in card.text.lower():
                    driver.execute_script("arguments[0].scrollIntoView(false);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    logger.info("Clicked Start Activity for Story Starter.", extra={'activity': 'StartActivity', 'step': 'start_clicked'})
                    found = True
                    break
            except Exception as e:
                continue
        if not found:
            logger.warning("No Story Starter activity found in Pending Activities.", extra={'activity': 'StartActivity', 'status': 'not_found'})
        else:
            logger.info("Activity started.", extra={'activity': 'StartActivity', 'status': 'started'})
        time.sleep(3)
    except Exception as e:
        logger.error(f"Failed to start Story Starter activity: {str(e)}", extra={'activity': 'StartActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def complete_story_starter(driver):
    try:
        logger.info("Starting story submission loop...", extra={'activity': 'CompleteActivity', 'step': 'start_loop'})
        wait = WebDriverWait(driver, 10)
        while True:
            try:
                # Wait for the text box to appear (adjust selector as needed)
                textbox = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[type='text']"))
                )
                logger.info("Text box found, entering text...", extra={'activity': 'CompleteActivity', 'step': 'textbox_found'})
                textbox.clear()
                textbox.send_keys('a')
                # Find the submit button (adjust selector as needed)
                submit_btn = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit my part')]")
                driver.execute_script("arguments[0].scrollIntoView(false);", submit_btn)
                time.sleep(0.5)
                submit_btn.click()
                logger.info("Clicked 'Submit my part' button.", extra={'activity': 'CompleteActivity', 'step': 'submit_clicked'})
                time.sleep(3)
            except Exception as e:
                logger.info("Text box no longer present or activity complete.", extra={'activity': 'CompleteActivity', 'status': 'finished'})
                break
    except Exception as e:
        logger.error(f"Error during story submission loop: {str(e)}", extra={'activity': 'CompleteActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    driver = None
    try:
        logger.info("--- Starting Student Story Starter Automation ---", extra={'activity': 'Main', 'status': 'started'})
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = "https://seeqlo-dev.vercel.app/login"
        driver.get(url)
        logger.info(f"Navigated to {url}", extra={'activity': 'Main', 'step': 'navigation'})
        email = "xyz@gmail.com"
        password = "hadi123"
        login(driver, email, password)
        logger.info("Starting student story starter activity...", extra={'activity': 'Main', 'status': 'activity_start'})
        start_story_starter_activity(driver)
        logger.info("Student story starter activity started successfully", extra={'activity': 'Main', 'status': 'activity_started'})

        # Loop: enter 'a' in text box, submit, repeat until text box is gone
        wait = WebDriverWait(driver, 10)
        while True:
            try:
                # Wait for the text box to appear (if not present, break)
                textbox = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[type='text']"))
                )
                logger.info("Text box found, entering 'a'...", extra={'activity': 'StoryGen', 'step': 'textbox_found'})
                textbox.clear()
                textbox.send_keys('a')
                # Find and click the 'Submit my part' button
                submit_btn = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit my part')]")
                driver.execute_script("arguments[0].scrollIntoView(false);", submit_btn)
                time.sleep(0.5)
                submit_btn.click()
                logger.info("Clicked 'Submit my part' button.", extra={'activity': 'StoryGen', 'step': 'submit_clicked'})
                time.sleep(10)
            except Exception as e:
                logger.info("Text box not found or activity complete.", extra={'activity': 'StoryGen', 'status': 'complete'})
                break

        logger.info("Student story starter activity completed", extra={'activity': 'Main', 'status': 'activity_completed'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
