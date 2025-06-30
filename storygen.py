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

def create_story_starter_assignment(driver):
    """
    Automates the creation of a Story Starter assignment.

    Args:
        driver: Selenium WebDriver instance.
    """
    wait = WebDriverWait(driver, 20) # Increased timeout for activity creation steps

    try:
        logger.info("Navigating to 'My Desk'...", extra={'activity': 'Story Starter', 'step': 'navigate_my_desk'})
        my_desk_span = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'My Desk')]")
        ))
        my_desk_span.click()
        logger.info("Automation script pressed 'My Desk' navigation link.", extra={'activity': 'Story Starter', 'step': 'my_desk_clicked'})
        time.sleep(2) # Allow page to settle after navigation

        logger.info("Clicking 'Story Starter' activity...", extra={'activity': 'Story Starter', 'step': 'clicking_activity'})
        story_starter = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'cursor-pointer')]//div[contains(., 'Story Starter')]") # Updated XPath for Story Starter
        ))
        story_starter.click()
        logger.info("Automation script pressed 'Story Starter' activity.", extra={'activity': 'Story Starter', 'step': 'activity_clicked'})
        time.sleep(2) # Allow activity page to load completely

        logger.info("Selecting class 'math grade 5 (2 students)'...", extra={'activity': 'Story Starter', 'step': 'selecting_class'})
        # Wait for the class dropdown to be present and visible
        class_dropdown_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//select[contains(@class, "w-full") and (./option[contains(text(), "-- Select Class --")] or ./option[contains(text(), "math grade 5 (2 students)")])]')))
        class_dropdown = Select(class_dropdown_element)
        class_dropdown.select_by_visible_text("math grade 5 (2 students)")
        logger.info("Automation script chose 'math grade 5 (2 students)' class for Story Starter.", extra={'activity': 'Story Starter', 'step': 'class_selected'})
        time.sleep(1) # Short pause after selection to allow UI updates

        # Scrolling logic for the main form container
        logger.info("Scrolling down the form to reveal hidden elements (if any)...", extra={'activity': 'Story Starter', 'step': 'scrolling_form'})
        try:
            scrollable_form = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'space-y-3') and contains(@class, 'lg:overflow-y-auto')]")
            ))
            for _ in range(3): # Scroll by 200px, three times
                driver.execute_script("arguments[0].scrollTop += 200;", scrollable_form)
                time.sleep(0.5) # Small pause between scrolls
            logger.info("Automation script scrolled down the form to reveal content.", extra={'activity': 'Story Starter', 'step': 'form_scrolled'})
        except Exception as e:
            logger.warning(f"Scroll of the main form content failed: {e}", extra={'activity': 'Story Starter', 'step': 'scroll_failed', 'warning_message': str(e)})
            driver.save_screenshot("scrolling_failed.png")


        logger.info("Clicking 'Generate Content' button...", extra={'activity': 'Story Starter', 'step': 'clicking_generate_content'})
        try:
            generate_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[./span[text()='Generate Content']]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", generate_btn)
            time.sleep(1)

            generate_btn.click()
            logger.info("Automation script clicked 'Generate Content' button.", extra={'activity': 'Story Starter', 'step': 'generate_content_clicked'})

            logger.info("Waiting 10 seconds for content generation by AI...", extra={'activity': 'Story Starter', 'step': 'waiting_for_ai_generation'})
            time.sleep(10) # Increased wait time for AI content generation

        except ElementClickInterceptedException as e:
            screenshot_path = "generate_button_intercepted.png"
            driver.save_screenshot(screenshot_path)
            logger.warning(f"Click on 'Generate Content' intercepted: {e}. Retrying with JS click.", extra={'activity': 'Story Starter', 'step': 'generate_content_intercepted', 'warning_message': str(e)})
            driver.execute_script("arguments[0].click();", generate_btn)
            logger.info("Automation script used JS to click 'Generate Content' after interception.", extra={'activity': 'Story Starter', 'step': 'generate_content_js_clicked'})
            time.sleep(10)
        except Exception as e:
            driver.save_screenshot("generate_button_error.png")
            logger.error(f"Failed to click 'Generate Content': {e}", extra={'activity': 'Story Starter', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
            raise

        logger.info("Clicking 'Assign to Class' button...", extra={'activity': 'Story Starter', 'step': 'clicking_assign_to_class'})
        try:
            assign_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Assign to Class')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", assign_btn)
            time.sleep(0.5)

            assign_btn.click()
            logger.info("Automation script successfully assigned the activity to the class.", extra={'activity': 'Story Starter', 'status': 'success'})
            time.sleep(3)

        except ElementClickInterceptedException as e:
            screenshot_path = "assign_button_intercepted_final.png"
            driver.save_screenshot(screenshot_path)
            logger.warning(f"Click on 'Assign to Class' intercepted: {e}. Retrying with JS click.", extra={'activity': 'Story Starter', 'step': 'assign_to_class_intercepted', 'warning_message': str(e)})
            driver.execute_script("arguments[0].click();", assign_btn)
            logger.info("Automation script used JS to click 'Assign to Class' after interception.", extra={'activity': 'Story Starter', 'step': 'assign_to_class_js_clicked'})
            time.sleep(3)
        except Exception as e:
            driver.save_screenshot("assign_button_error_final.png")
            logger.error(f"Failed to click 'Assign to Class': {e}", extra={'activity': 'Story Starter', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
            raise

    except Exception as e:
        driver.save_screenshot("story_starter_full_error.png") # Updated screenshot name
        logger.error(f"Critical error during Story Starter assignment: {e}", extra={'activity': 'Story Starter', 'status': 'critical_failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    """
    Main function to initialize the browser, perform login,
    and create the Story Starter assignment.
    """
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()

        email = "ibadt@gmail.com"
        password = "ibad1234"

        login(driver, email, password)
        logger.info("--- Starting Story Starter Assignment Automation ---", extra={'activity': 'Main', 'status': 'started'})
        create_story_starter_assignment(driver)
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
