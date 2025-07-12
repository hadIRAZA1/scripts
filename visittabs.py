import logging
import time
import traceback
import json
from pythonjsonlogger import jsonlogger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, ElementNotInteractableException

# Logger setup
logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Remove existing handlers from the root logger if basicConfig was called previously
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Custom formatter for JSON output
json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')

# Create a handler to write to a file, ensuring append mode ('a')
log_file_handler = logging.FileHandler('automation_logs.json', mode='a')
log_file_handler.setFormatter(json_formatter)

# Create a stream handler for console output with a standard format
stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)

# Get the logger and add handlers
logger = logging.getLogger("TabVisitingAutomation")
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)
logger.addHandler(stream_handler)

BASE_URL = "https://seeqlo-dev.vercel.app"

def login(driver, email, password):
    """
    Handles the login process for the application.
    """
    try:
        logger.info("Starting login process.", extra={'activity': 'Login', 'step': 'init'})
        driver.get(BASE_URL + "/login")
        wait = WebDriverWait(driver, 20)

        logger.info("Entering email...", extra={'activity': 'Login', 'step': 'entering_email'})
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@placeholder, 'example.com')]")))
        email_input.send_keys(email)
        logger.info("Email entered.", extra={'activity': 'Login', 'step': 'email_entered'})

        logger.info("Entering password...", extra={'activity': 'Login', 'step': 'entering_password'})
        password_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
        password_input.send_keys(password)
        logger.info("Password entered.", extra={'activity': 'Login', 'step': 'password_entered'})

        logger.info("Clicking login button...", extra={'activity': 'Login', 'step': 'clicking_login_button'})
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]")))
        login_btn.click()
        logger.info("Login button clicked.", extra={'activity': 'Login', 'step': 'login_button_clicked'})

        logger.info("Waiting for dashboard...", extra={'activity': 'Login', 'step': 'waiting_dashboard'})
        wait.until(EC.url_changes(BASE_URL + "/login"))
        wait.until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space(.)='Welcome back, ibadt']")))
        logger.info("Login successful. Dashboard loaded.", extra={'activity': 'Login', 'status': 'success'})

    except Exception as e:
        driver.save_screenshot("selenium_login_error.png")
        logger.error(f"Login error: {e}", extra={'activity': 'Login', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def test_navigation_tabs(driver):
    """
    Quickly tests all main navigation tabs for responsiveness.
    """
    wait = WebDriverWait(driver, 20)
    
    # List of main navigation tabs to test
    navigation_tabs = [
        "Dashboard",
        "Classroom", 
        "My Desk",
        "History",
        "Feedback"
    ]
    
    for tab in navigation_tabs:
        try:
            logger.info(f"Testing navigation tab: {tab}", extra={'activity': 'Navigation Test', 'step': f'test_{tab.lower().replace(" ", "_")}'})
            
            # Click on the navigation tab
            tab_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), '{tab}')]")
            ))
            tab_link.click()
            logger.info(f"Navigation tab '{tab}' clicked successfully.", extra={'activity': 'Navigation Test', 'step': f'{tab.lower().replace(" ", "_")}_clicked'})
            
            # Quick wait to ensure page loads
            time.sleep(2)
            logger.info(f"Navigation tab '{tab}' is responsive.", extra={'activity': 'Navigation Test', 'step': f'{tab.lower().replace(" ", "_")}_responsive'})
            
        except Exception as e:
            driver.save_screenshot(f"{tab.lower().replace(' ', '_')}_error.png")
            logger.error(f"Error testing navigation tab {tab}: {e}", extra={'activity': 'Navigation Test', 'step': f'{tab.lower().replace(" ", "_")}_error', 'error_message': str(e)})
            # Continue testing other tabs even if one fails
    
    logger.info("All navigation tabs tested.", extra={'activity': 'Navigation Test', 'status': 'completed'})

def main():
    """
    Main function to initialize the browser, perform login,
    and test all navigation tabs for responsiveness.
    """
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()

        email = "ibadt@gmail.com"
        password = "ibad1234"

        login(driver, email, password)
        logger.info("--- Starting Navigation Tab Responsiveness Test ---", extra={'activity': 'Main', 'status': 'started'})
        
        # Test all navigation tabs
        test_navigation_tabs(driver)
        
        logger.info("Navigation responsiveness test completed successfully.", extra={'activity': 'Main', 'status': 'completed'})
        
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
