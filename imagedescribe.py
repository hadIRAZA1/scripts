import logging
import time
import traceback
import json # Import json for writing to file
from pythonjsonlogger import jsonlogger # Import jsonlogger
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
# This prevents duplicate logs if the script is run multiple times in the same process
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
logger = logging.getLogger("AssignmentAutomation")
logger.setLevel(logging.INFO) # Set the logging level to INFO or DEBUG for more verbosity
logger.addHandler(log_file_handler)
logger.addHandler(stream_handler) # Add stream handler for console output


BASE_URL = "https://seeqlo-dev.vercel.app"

def login(driver, email, password):
    """
    Handles the login process for the application.

    Args:
        driver: Selenium WebDriver instance.
        email (str): User's email for login.
        password (str): User's password for login.
    """
    try:
        logger.info("Starting login process.", extra={'activity': 'Login', 'step': 'init'})
        driver.get(BASE_URL + "/login")
        wait = WebDriverWait(driver, 20) # Increased timeout for login page load

        logger.info("Entering email...", extra={'activity': 'Login', 'step': 'entering_email'})
        # Wait for the email input field to be present and visible
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@placeholder, 'example.com')]")))
        email_input.send_keys(email)
        logger.info("Email entered.", extra={'activity': 'Login', 'step': 'email_entered'})

        logger.info("Entering password...", extra={'activity': 'Login', 'step': 'entering_password'})
        # Wait for the password input field to be present and visible
        password_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
        password_input.send_keys(password)
        logger.info("Password entered.", extra={'activity': 'Login', 'step': 'password_entered'})

        logger.info("Clicking login button...", extra={'activity': 'Login', 'step': 'clicking_login_button'})
        # Wait for the login button to be clickable
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]")))
        login_btn.click()
        logger.info("Login button clicked.", extra={'activity': 'Login', 'step': 'login_button_clicked'})

        logger.info("Waiting for dashboard...", extra={'activity': 'Login', 'step': 'waiting_dashboard'})
        # Wait until the URL changes from login and a specific dashboard element is present
        wait.until(EC.url_changes(BASE_URL + "/login"))
        wait.until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space(.)='Welcome back, ibadt']")))
        logger.info("Login successful. Dashboard loaded.", extra={'activity': 'Login', 'status': 'success'})

    except Exception as e:
        driver.save_screenshot("selenium_login_error.png") # Capture screenshot on error
        logger.error(f"Login error: {e}", extra={'activity': 'Login', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise # Re-raise the exception to stop the script on critical failure

def create_image_describe_assignment(driver): # Renamed function to reflect "Image Describe"
    """
    Automates the creation of an Image Describe assignment.

    Args:
        driver: Selenium WebDriver instance.
    """
    wait = WebDriverWait(driver, 20) # Increased timeout for activity creation steps

    try:
        logger.info("Navigating to 'My Desk'...", extra={'activity': 'Image Describe', 'step': 'navigate_my_desk'})
        my_desk_span = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'My Desk')]")
        ))
        my_desk_span.click()
        logger.info("Automation script pressed 'My Desk' navigation link.", extra={'activity': 'Image Describe', 'step': 'my_desk_clicked'})
        time.sleep(2) # Allow page to settle after navigation

        logger.info("Clicking 'Image Describe' activity...", extra={'activity': 'Image Describe', 'step': 'clicking_activity'})
        image_describe = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'cursor-pointer')]//div[contains(., 'Image Describe')]") # Corrected XPath for Image Describe
        ))
        image_describe.click()
        logger.info("Automation script pressed 'Image Describe' activity.", extra={'activity': 'Image Describe', 'step': 'activity_clicked'})
        time.sleep(2) # Allow activity page to load completely

        logger.info("Selecting class 'math grade 5 (2 students)'...", extra={'activity': 'Image Describe', 'step': 'selecting_class'})
        # Wait for the class dropdown to be present and visible
        class_dropdown_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//select[contains(@class, "w-full") and (./option[contains(text(), "-- Select Class --")] or ./option[contains(text(), "math grade 5 (2 students)")])]')))
        class_dropdown = Select(class_dropdown_element)
        class_dropdown.select_by_visible_text("math grade 5 (2 students)")
        logger.info("Automation script chose 'math grade 5 (2 students)' class for Image Describe.", extra={'activity': 'Image Describe', 'step': 'class_selected'})
        time.sleep(1) # Short pause after selection to allow UI updates

        # Scrolling logic for the main form container (if any elements below are hidden)
        logger.info("Scrolling down the form to reveal hidden elements (if any)...", extra={'activity': 'Image Describe', 'step': 'scrolling_form'})
        try:
            scrollable_form = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'space-y-3') and contains(@class, 'lg:overflow-y-auto')]")
            ))
            for _ in range(3): # Scroll by 200px, three times
                driver.execute_script("arguments[0].scrollTop += 200;", scrollable_form)
                time.sleep(0.5) # Small pause between scrolls
            logger.info("Automation script scrolled down the form to reveal content.", extra={'activity': 'Image Describe', 'step': 'form_scrolled'})
        except Exception as e:
            logger.warning(f"Scroll of the main form content failed: {e}", extra={'activity': 'Image Describe', 'step': 'scroll_failed', 'warning_message': str(e)})
            driver.save_screenshot("scrolling_failed.png")


        # Removed 'Generate Content' section as per user's request for this activity

        logger.info("Clicking 'Assign to Class' button directly...", extra={'activity': 'Image Describe', 'step': 'clicking_assign_to_class'})
        try:
            assign_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Assign to Class')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", assign_btn)
            time.sleep(0.5)

            assign_btn.click()
            logger.info("Automation script successfully assigned the 'Image Describe' activity to the class.", extra={'activity': 'Image Describe', 'status': 'success'})
            time.sleep(3)

        except ElementClickInterceptedException as e:
            screenshot_path = "assign_button_intercepted_final.png"
            driver.save_screenshot(screenshot_path)
            logger.warning(f"Click on 'Assign to Class' intercepted: {e}. Retrying with JS click.", extra={'activity': 'Image Describe', 'step': 'assign_to_class_intercepted', 'warning_message': str(e)})
            driver.execute_script("arguments[0].click();", assign_btn)
            logger.info("Automation script used JS to click 'Assign to Class' after interception.", extra={'activity': 'Image Describe', 'step': 'assign_to_class_js_clicked'})
            time.sleep(3)
        except Exception as e:
            driver.save_screenshot("assign_button_error_final.png")
            logger.error(f"Failed to click 'Assign to Class': {e}", extra={'activity': 'Image Describe', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
            raise

    except Exception as e:
        driver.save_screenshot("image_describe_full_error.png") # Updated screenshot name
        logger.error(f"Critical error during Image Describe assignment: {e}", extra={'activity': 'Image Describe', 'status': 'critical_failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    """
    Main function to initialize the browser, perform login,
    and create the Image Describe assignment.
    """
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()

        email = "ibadt@gmail.com"
        password = "ibad1234"

        login(driver, email, password)
        logger.info("--- Starting Image Describe Assignment Automation ---", extra={'activity': 'Main', 'status': 'started'})
        create_image_describe_assignment(driver) # Updated function call
        logger.info("Automation script finished successfully.", extra={'activity': 'Main', 'status': 'completed'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
