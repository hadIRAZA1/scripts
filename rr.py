import logging
import time
import traceback
from pythonjsonlogger import jsonlogger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
logger = logging.getLogger("StudentReadRespond")
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

def start_read_respond_activity(driver):
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
        logger.info("Looking for Read and Respond activity in Pending Activities...", extra={'activity': 'StartActivity', 'step': 'find_read_respond'})
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(1)
        start_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Start Activity') or contains(text(), 'Start')]")
        found = False
        for btn in start_buttons:
            try:
                card = btn.find_element(By.XPATH, "ancestor::div[contains(@class, 'flex')][1]")
                if 'read and respond' in card.text.lower():
                    driver.execute_script("arguments[0].scrollIntoView(false);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    logger.info("Clicked Start Activity for Read and Respond.", extra={'activity': 'StartActivity', 'step': 'start_clicked'})
                    found = True
                    break
            except Exception as e:
                continue
        if not found:
            logger.warning("No Read and Respond activity found in Pending Activities.", extra={'activity': 'StartActivity', 'status': 'not_found'})
        else:
            logger.info("Activity started.", extra={'activity': 'StartActivity', 'status': 'started'})
        time.sleep(3)
    except Exception as e:
        logger.error(f"Failed to start Read and Respond activity: {str(e)}", extra={'activity': 'StartActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def complete_read_respond(driver):
    try:
        logger.info("Starting Read and Respond loop...", extra={'activity': 'CompleteActivity', 'step': 'start_loop'})
        wait = WebDriverWait(driver, 10)
        while True:
            # Check for score at the bottom
            try:
                score_elem = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'score')]")
                if score_elem.is_displayed():
                    logger.info("Score detected, activity complete.", extra={'activity': 'CompleteActivity', 'status': 'finished'})
                    break
            except Exception:
                pass
            try:
                # Wait for two text boxes
                textboxes = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "textarea, input[type='text']"))
                )
                if len(textboxes) < 2:
                    logger.warning("Less than 2 text boxes found.", extra={'activity': 'CompleteActivity', 'step': 'textbox_count'})
                    break
                logger.info("Text boxes found, entering text...", extra={'activity': 'CompleteActivity', 'step': 'textbox_found'})
                for textbox in textboxes[:2]:
                    textbox.clear()
                    textbox.send_keys('a')
                # Find the green 'Submit Answer' button
                submit_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'bg-green') or contains(@class, 'bg-success') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit answer')]")
                driver.execute_script("arguments[0].scrollIntoView(false);", submit_btn)
                time.sleep(0.5)
                submit_btn.click()
                logger.info("Clicked 'Submit Answer' button.", extra={'activity': 'CompleteActivity', 'step': 'submit_clicked'})
                time.sleep(2)
                # Click 'Next Passage' if available
                try:
                    next_btn = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next passage')]")
                    if next_btn.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(false);", next_btn)
                        time.sleep(0.5)
                        next_btn.click()
                        logger.info("Clicked 'Next Passage' button.", extra={'activity': 'CompleteActivity', 'step': 'next_passage_clicked'})
                        time.sleep(2)
                except Exception:
                    logger.info("No 'Next Passage' button found, checking for score...", extra={'activity': 'CompleteActivity', 'step': 'no_next_passage'})
            except Exception as e:
                logger.info("Text boxes not found or activity complete.", extra={'activity': 'CompleteActivity', 'status': 'finished'})
                break
    except Exception as e:
        logger.error(f"Error during Read and Respond loop: {str(e)}", extra={'activity': 'CompleteActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    driver = None
    try:
        logger.info("--- Starting Student Read and Respond Automation ---", extra={'activity': 'Main', 'status': 'started'})
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = "https://seeqlo-dev.vercel.app/login"
        driver.get(url)
        logger.info(f"Navigated to {url}", extra={'activity': 'Main', 'step': 'navigation'})
        email = "xyz@gmail.com"
        password = "hadi123"
        login(driver, email, password)
        logger.info("Starting student Read and Respond activity...", extra={'activity': 'Main', 'status': 'activity_start'})
        start_read_respond_activity(driver)
        logger.info("Student Read and Respond activity started successfully", extra={'activity': 'Main', 'status': 'activity_started'})
        complete_read_respond(driver)
        logger.info("Student Read and Respond activity completed", extra={'activity': 'Main', 'status': 'activity_completed'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
