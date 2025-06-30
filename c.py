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
logger = logging.getLogger("StudentCurrency")
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)
logger.addHandler(stream_handler)

def login(driver, email, password):
    try:
        logger.info("Starting login process.", extra={'activity': 'Login', 'step': 'init'})
        wait = WebDriverWait(driver, 15)
        email_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.clear()
        email_input.send_keys(email)
        logger.info("Email entered.", extra={'activity': 'Login', 'step': 'email_entered'})
        password_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        password_input.clear()
        password_input.send_keys(password)
        logger.info("Password entered.", extra={'activity': 'Login', 'step': 'password_entered'})
        login_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_button.click()
        logger.info("Login button clicked.", extra={'activity': 'Login', 'step': 'login_button_clicked'})
        # Wait for dashboard or nav to appear
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav"))
        )
        logger.info("Successfully logged in.", extra={'activity': 'Login', 'status': 'success'})
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", extra={'activity': 'Login', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def start_currency_activity(driver):
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
        logger.info("Looking for Currency activity in Pending Activities...", extra={'activity': 'StartActivity', 'step': 'find_currency'})
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(1)
        start_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Start Activity') or contains(text(), 'Start')]")
        found = False
        for btn in start_buttons:
            try:
                card = btn.find_element(By.XPATH, "ancestor::div[contains(@class, 'flex')][1]")
                if 'currency' in card.text.lower():
                    driver.execute_script("arguments[0].scrollIntoView(false);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    logger.info("Clicked Start Activity for Currency.", extra={'activity': 'StartActivity', 'step': 'start_clicked'})
                    found = True
                    break
            except Exception as e:
                continue
        if not found:
            logger.warning("No Currency activity found in Pending Activities.", extra={'activity': 'StartActivity', 'status': 'not_found'})
        else:
            logger.info("Activity started.", extra={'activity': 'StartActivity', 'status': 'started'})
        time.sleep(3)
    except Exception as e:
        logger.error(f"Failed to start Currency activity: {str(e)}", extra={'activity': 'StartActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def complete_currency_activity(driver):
    try:
        logger.info("Starting Currency activity...", extra={'activity': 'CompleteActivity', 'step': 'start'})
        wait = WebDriverWait(driver, 10)
        # Skip pressing any bill, just press Check Answer
        check_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'check answer')]")
        ))
        driver.execute_script("arguments[0].scrollIntoView(false);", check_btn)
        time.sleep(0.5)
        check_btn.click()
        logger.info("Clicked 'Check Answer' button.", extra={'activity': 'CompleteActivity', 'step': 'check_answer_clicked'})
        time.sleep(2)
        # Review summary (wait for summary or completion message)
        try:
            summary = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'summary') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'completed') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'score')]")
            ))
            logger.info("Review summary or completion detected.", extra={'activity': 'CompleteActivity', 'step': 'summary_detected'})
        except Exception:
            logger.warning("No summary or completion message found.", extra={'activity': 'CompleteActivity', 'step': 'no_summary'})
        logger.info("Currency activity completed.", extra={'activity': 'CompleteActivity', 'status': 'finished'})
    except Exception as e:
        logger.error(f"Error during Currency activity: {str(e)}", extra={'activity': 'CompleteActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    driver = None
    try:
        logger.info("--- Starting Student Currency Automation ---", extra={'activity': 'Main', 'status': 'started'})
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = "https://seeqlo-dev.vercel.app/login"
        driver.get(url)
        logger.info(f"Navigated to {url}", extra={'activity': 'Main', 'step': 'navigation'})
        email = "xyz@gmail.com"
        password = "hadi123"
        login(driver, email, password)
        logger.info("Starting student Currency activity...", extra={'activity': 'Main', 'status': 'activity_start'})
        start_currency_activity(driver)
        logger.info("Student Currency activity started successfully", extra={'activity': 'Main', 'status': 'activity_started'})
        complete_currency_activity(driver)
        logger.info("Student Currency activity completed", extra={'activity': 'Main', 'status': 'activity_completed'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
