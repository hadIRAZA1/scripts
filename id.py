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
logger = logging.getLogger("StudentImageDescribe")
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

def start_image_describe_activity(driver):
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
        logger.info("Looking for Image Describe activity in Pending Activities...", extra={'activity': 'StartActivity', 'step': 'find_image_describe'})
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(1)
        start_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Start Activity') or contains(text(), 'Start')]")
        found = False
        for btn in start_buttons:
            try:
                card = btn.find_element(By.XPATH, "ancestor::div[contains(@class, 'flex')][1]")
                if 'image describe' in card.text.lower():
                    driver.execute_script("arguments[0].scrollIntoView(false);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    logger.info("Clicked Start Activity for Image Describe.", extra={'activity': 'StartActivity', 'step': 'start_clicked'})
                    found = True
                    break
            except Exception as e:
                continue
        if not found:
            logger.warning("No Image Describe activity found in Pending Activities.", extra={'activity': 'StartActivity', 'status': 'not_found'})
        else:
            logger.info("Activity started.", extra={'activity': 'StartActivity', 'status': 'started'})
        time.sleep(3)
    except Exception as e:
        logger.error(f"Failed to start Image Describe activity: {str(e)}", extra={'activity': 'StartActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def complete_image_describe(driver):
    try:
        logger.info("Starting Image Describe activity...", extra={'activity': 'CompleteActivity', 'step': 'start'})
        wait = WebDriverWait(driver, 10)
        # Click the blue 'New Image' button
        new_image_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'bg-blue') or contains(@class, 'bg-primary') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'new image')]")
        ))
        driver.execute_script("arguments[0].scrollIntoView(false);", new_image_btn)
        time.sleep(0.5)
        new_image_btn.click()
        logger.info("Clicked 'New Image' button.", extra={'activity': 'CompleteActivity', 'step': 'new_image_clicked'})
        time.sleep(8)
        # Enter 'a' in all text boxes
        textboxes = driver.find_elements(By.CSS_SELECTOR, "textarea, input[type='text']")
        if not textboxes:
            logger.warning("No text boxes found after new image.", extra={'activity': 'CompleteActivity', 'step': 'no_textboxes'})
        else:
            for textbox in textboxes:
                textbox.clear()
                textbox.send_keys('a')
            logger.info("Entered 'a' in all text boxes.", extra={'activity': 'CompleteActivity', 'step': 'textboxes_filled'})
        # Optionally, click a submit button if required (add logic if needed)
        logger.info("Image Describe activity completed.", extra={'activity': 'CompleteActivity', 'status': 'finished'})
    except Exception as e:
        logger.error(f"Error during Image Describe activity: {str(e)}", extra={'activity': 'CompleteActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    driver = None
    try:
        logger.info("--- Starting Student Image Describe Automation ---", extra={'activity': 'Main', 'status': 'started'})
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = "https://seeqlo-dev.vercel.app/login"
        driver.get(url)
        logger.info(f"Navigated to {url}", extra={'activity': 'Main', 'step': 'navigation'})
        email = "xyz@gmail.com"
        password = "hadi123"
        login(driver, email, password)
        logger.info("Starting student Image Describe activity...", extra={'activity': 'Main', 'status': 'activity_start'})
        start_image_describe_activity(driver)
        logger.info("Student Image Describe activity started successfully", extra={'activity': 'Main', 'status': 'activity_started'})
        complete_image_describe(driver)
        logger.info("Student Image Describe activity completed", extra={'activity': 'Main', 'status': 'activity_completed'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
