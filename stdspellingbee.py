import logging
import time
import traceback
from pythonjsonlogger import jsonlogger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Logger setup (same as spellingbee.py)
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
logger = logging.getLogger("StudentSpellingBee")
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

def start_pending_activity(driver):
    try:
        logger.info("Waiting for Classroom tab to be clickable...", extra={'activity': 'StartActivity', 'step': 'wait_classroom_tab'})
        wait = WebDriverWait(driver, 20)
        # Try to find the Classroom tab by span (like 'My Desk' in teacher version)
        try:
            classroom_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'Classroom')]"))
            )
        except Exception:
            # Fallback: try anchor with text
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
        logger.info("Looking for Spelling Bee activity in Pending Activities...", extra={'activity': 'StartActivity', 'step': 'find_spellingbee'})
        # Find all Start Activity buttons under Pending Activities
        start_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Start Activity') or contains(text(), 'Start')]")
        found = False
        for btn in start_buttons:
            try:
                # Go up to the card container and check for 'Spelling Bee' heading
                card = btn.find_element(By.XPATH, "ancestor::div[contains(@class, 'flex')][1]")
                if 'Spelling Bee' in card.text:
                    driver.execute_script("arguments[0].scrollIntoView(false);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    logger.info("Clicked Start Activity for Spelling Bee.", extra={'activity': 'StartActivity', 'step': 'start_clicked'})
                    found = True
                    break
            except Exception as e:
                continue
        if not found:
            logger.warning("No Spelling Bee activity found in Pending Activities.", extra={'activity': 'StartActivity', 'status': 'not_found'})
        else:
            logger.info("Activity started.", extra={'activity': 'StartActivity', 'status': 'started'})

        time.sleep(3)
    except Exception as e:
        logger.error(f"Failed to start activity: {str(e)}", extra={'activity': 'StartActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def complete_spelling_bee(driver):
    try:
        wait = WebDriverWait(driver, 15)
        answers = ['a', 'b', 'c']
        for idx, answer in enumerate(answers):
            logger.info(f"Attempting word {idx+1} of 3...", extra={'activity': 'SpellingBee', 'step': f'word_{idx+1}'})
            # Wait for the input box to be visible
            input_box = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Type the word here...']")))
            input_box.clear()
            input_box.send_keys(answer)
            logger.info(f"Entered '{answer}' in the input box.", extra={'activity': 'SpellingBee', 'step': f'word_{idx+1}_entered'})
            # Wait for the submit button to be enabled/clickable
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Submit Answer')]")))
            driver.execute_script("arguments[0].click();", submit_btn)
            logger.info("Clicked Submit Answer.", extra={'activity': 'SpellingBee', 'step': f'word_{idx+1}_submitted'})
            # Wait for the Next Word button and click it, except after the last answer
            if idx < len(answers) - 1:
                logger.info("Waiting for Next Word button...", extra={'activity': 'SpellingBee', 'step': f'word_{idx+1}_next'})
                next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Next Word')]")))
                driver.execute_script("arguments[0].click();", next_btn)
                logger.info("Clicked Next Word.", extra={'activity': 'SpellingBee', 'step': f'word_{idx+1}_next_clicked'})
                time.sleep(1)
            time.sleep(1)
        # After last answer, click Next Word one more time
        logger.info("Waiting for final Next Word button...", extra={'activity': 'SpellingBee', 'step': 'final_next'})
        final_next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Next Word')]")))
        driver.execute_script("arguments[0].click();", final_next_btn)
        logger.info("Clicked final Next Word. Waiting 5 seconds before finishing.", extra={'activity': 'SpellingBee', 'step': 'final_next_clicked'})
        time.sleep(5)
        logger.info("Completed all spelling bee answers.", extra={'activity': 'SpellingBee', 'status': 'completed'})
    except Exception as e:
        logger.error(f"Failed to complete spelling bee: {str(e)}", extra={'activity': 'SpellingBee', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    driver = None
    try:
        logger.info("--- Starting Student Spelling Bee Automation ---", extra={'activity': 'Main', 'status': 'started'})
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = "https://seeqlo-dev.vercel.app/login"
        driver.get(url)
        logger.info(f"Navigated to {url}", extra={'activity': 'Main', 'step': 'navigation'})
        email = "xyz@gmail.com"
        password = "hadi123"
        login(driver, email, password)
        logger.info("Starting student spelling bee activity...", extra={'activity': 'Main', 'status': 'activity_start'})
        start_pending_activity(driver)
        logger.info("Student activity started successfully", extra={'activity': 'Main', 'status': 'activity_started'})
        complete_spelling_bee(driver)
        logger.info("Spelling bee answers submitted.", extra={'activity': 'Main', 'status': 'answers_submitted'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
