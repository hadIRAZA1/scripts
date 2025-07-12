import logging
import time
import traceback
from pythonjsonlogger import jsonlogger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, ElementNotInteractableException

# Logger setup
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
logger = logging.getLogger("StudentTabVisitingAutomation")
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)
logger.addHandler(stream_handler)

BASE_URL = "https://seeqlo-dev.vercel.app"

def login(driver, email, password):
    try:
        logger.info("Starting login process.", extra={'activity': 'Login', 'step': 'init'})
        driver.get(BASE_URL + "/login")
        wait = WebDriverWait(driver, 20)
        logger.info("Waiting for email input...", extra={'activity': 'Login', 'step': 'waiting_email_input'})
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        email_input.clear()
        email_input.send_keys(email)
        logger.info("Email entered.", extra={'activity': 'Login', 'step': 'email_entered'})
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        password_input.clear()
        password_input.send_keys(password)
        logger.info("Password entered.", extra={'activity': 'Login', 'step': 'password_entered'})
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        logger.info("Login button clicked.", extra={'activity': 'Login', 'step': 'login_button_clicked'})
        # Wait for nav element to confirm login
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
        logger.info("Login successful. Navigation bar loaded.", extra={'activity': 'Login', 'status': 'success'})
    except Exception as e:
        driver.save_screenshot("selenium_login_error.png")
        logger.error(f"Login error: {e}", extra={'activity': 'Login', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def test_navigation_tabs(driver):
    wait = WebDriverWait(driver, 20)
    navigation_tabs = [
        "Dashboard",
        "Classroom",
        "Practice",
        "Student Feedback"
    ]
    for tab in navigation_tabs:
        try:
            logger.info(f"Testing navigation tab: {tab}", extra={'activity': 'Navigation Test', 'step': f'test_{tab.lower().replace(" ", "_")}'})
            tab_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), '{tab}')]")
            ))
            tab_link.click()
            logger.info(f"Navigation tab '{tab}' clicked successfully.", extra={'activity': 'Navigation Test', 'step': f'{tab.lower().replace(" ", "_")}_clicked'})
            time.sleep(2)
            logger.info(f"Navigation tab '{tab}' is responsive.", extra={'activity': 'Navigation Test', 'step': f'{tab.lower().replace(" ", "_")}_responsive'})
        except Exception as e:
            driver.save_screenshot(f"{tab.lower().replace(' ', '_')}_error.png")
            logger.error(f"Error testing navigation tab {tab}: {e}", extra={'activity': 'Navigation Test', 'step': f'{tab.lower().replace(" ", "_")}_error', 'error_message': str(e)})
    logger.info("All navigation tabs tested.", extra={'activity': 'Navigation Test', 'status': 'completed'})

def main():
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()
        email = "xyz@gmail.com"
        password = "hadi123"
        login(driver, email, password)
        logger.info("--- Starting Student Navigation Tab Responsiveness Test ---", extra={'activity': 'Main', 'status': 'started'})
        test_navigation_tabs(driver)
        logger.info("Student navigation responsiveness test completed successfully.", extra={'activity': 'Main', 'status': 'completed'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
