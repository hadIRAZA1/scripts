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
logger = logging.getLogger("TeacherSpellingBee")
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
        logger.info("Login button clicked.", extra={'activity': 'Login', 'step': 'login_button_clicked'}) # Corrected: 'licked' to 'clicked'
        logger.info("Waiting for dashboard...", extra={'activity': 'Login', 'step': 'waiting_dashboard'})
        # Wait until the URL changes from login and a specific dashboard element is present
        wait.until(EC.url_changes(BASE_URL + "/login"))
        wait.until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space(.)='Welcome back, ibadt']")))
        logger.info("Login successful. Dashboard loaded.", extra={'activity': 'Login', 'status': 'success'})

    except Exception as e:
        driver.save_screenshot("selenium_login_error.png") # Capture screenshot on error
        logger.error(f"Login error: {e}", extra={'activity': 'Login', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise # Re-raise the exception to stop the script on critical failure

def create_spelling_bee_assignment(driver):
    """
    Automates the creation of a Spelling Bee assignment.

    Args:
        driver: Selenium WebDriver instance.
    """
    wait = WebDriverWait(driver, 20) # Increased timeout for activity creation steps

    try:
        logger.info("Navigating to 'My Desk'...", extra={'activity': 'Spelling Bee', 'step': 'navigate_my_desk'})
        my_desk_span = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'My Desk')]")
        ))
        my_desk_span.click()
        logger.info("Automation script pressed 'My Desk' navigation link.", extra={'activity': 'Spelling Bee', 'step': 'my_desk_clicked'})
        time.sleep(2) # Allow page to settle after navigation

        logger.info("Clicking 'Spelling Bee' activity...", extra={'activity': 'Spelling Bee', 'step': 'clicking_activity'})
        spelling_bee = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'cursor-pointer')]//div[contains(., 'Spelling Bee')]")
        ))
        spelling_bee.click()
        logger.info("Automation script pressed 'Spelling Bee' activity.", extra={'activity': 'Spelling Bee', 'step': 'activity_clicked'})
        time.sleep(2) # Allow activity page to load completely

        logger.info("Selecting class 'math grade 5 (3 students)'...", extra={'activity': 'Spelling Bee', 'step': 'selecting_class'})
        # Wait for the class dropdown to be present and visible
        class_dropdown_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//select[contains(@class, "w-full") and (./option[contains(text(), "-- Select Class --")] or ./option[contains(text(), "math grade 5 (3 students)")])]')))
        class_dropdown = Select(class_dropdown_element)
        class_dropdown.select_by_visible_text("math grade 5 (3 students)")
        logger.info("Automation script chose 'math grade 5 (2 students)' class for Spelling Bee.", extra={'activity': 'Spelling Bee', 'step': 'class_selected'})
        time.sleep(1) # Short pause after selection to allow UI updates

        # Re-introducing scrolling logic for the main form container
        logger.info("Scrolling down the form to reveal hidden elements (if any)...", extra={'activity': 'Spelling Bee', 'step': 'scrolling_form'})
        try:
            # Target the specific scrollable div based on the provided HTML structure (from image)
            scrollable_form = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'space-y-3') and contains(@class, 'lg:overflow-y-auto')]")
            ))
            # Scroll down multiple times to ensure visibility of all elements in the form
            for _ in range(3): # Scroll by 200px, three times
                driver.execute_script("arguments[0].scrollTop += 200;", scrollable_form)
                time.sleep(0.5) # Small pause between scrolls
            logger.info("Automation script scrolled down the form to reveal content.", extra={'activity': 'Spelling Bee', 'step': 'form_scrolled'})
        except Exception as e:
            logger.warning(f"Scroll of the main form content failed: {e}", extra={'activity': 'Spelling Bee', 'step': 'scroll_failed', 'warning_message': str(e)})
            driver.save_screenshot("scrolling_failed.png")


        logger.info("Clicking 'Generate Content' button...", extra={'activity': 'Spelling Bee', 'step': 'clicking_generate_content'})
        try:
            # Wait for the Generate Content button to be clickable
            generate_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[./span[text()='Generate Content']]")
            ))
            # Ensure it's in view just before clicking, as modals might shift
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", generate_btn)
            time.sleep(1) # Increased pause before clicking Generate Content

            generate_btn.click()
            logger.info("Automation script clicked 'Generate Content' button.", extra={'activity': 'Spelling Bee', 'step': 'generate_content_clicked'})

            logger.info("Waiting 10 seconds for content generation by AI...", extra={'activity': 'Spelling Bee', 'step': 'waiting_for_ai_generation'})
            time.sleep(15) # Increased wait time for AI content generation

        except ElementClickInterceptedException as e:
            screenshot_path = "generate_button_intercepted.png"
            driver.save_screenshot(screenshot_path)
            logger.warning(f"Click on 'Generate Content' intercepted: {e}. Retrying with JS click.", extra={'activity': 'Spelling Bee', 'step': 'generate_content_intercepted', 'warning_message': str(e)})
            # Force click with JavaScript if intercepted
            driver.execute_script("arguments[0].click();", generate_btn)
            logger.info("Automation script used JS to click 'Generate Content' after interception.", extra={'activity': 'Spelling Bee', 'step': 'generate_content_js_clicked'})
            time.sleep(10) # Increased wait time for AI content generation
        except Exception as e:
            driver.save_screenshot("generate_button_error.png")
            logger.error(f"Failed to click 'Generate Content': {e}", extra={'activity': 'Spelling Bee', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
            raise # Critical step, re-raise

        logger.info("Clicking 'Assign to Class' button...", extra={'activity': 'Spelling Bee', 'step': 'clicking_assign_to_class'})
        try:
            # Wait for the Assign to Class button to be clickable
            assign_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Assign to Class')]")
            ))
            # Ensure it's in view if not already
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", assign_btn)
            time.sleep(0.5) # Short pause after ensuring visibility

            assign_btn.click()
            logger.info("Automation script successfully assigned the activity to the class.", extra={'activity': 'Spelling Bee', 'status': 'success'})
            time.sleep(3) # Final brief pause to see the success state

        except ElementClickInterceptedException as e:
            screenshot_path = "assign_button_intercepted_final.png"
            driver.save_screenshot(screenshot_path)
            logger.warning(f"Click on 'Assign to Class' intercepted: {e}. Retrying with JS click.", extra={'activity': 'Spelling Bee', 'step': 'assign_to_class_intercepted', 'warning_message': str(e)})
            driver.execute_script("arguments[0].click();", assign_btn) # Force click with JS
            logger.info("Automation script used JS to click 'Assign to Class' after interception.", extra={'activity': 'Spelling Bee', 'step': 'assign_to_class_js_clicked'})
            time.sleep(3) # Final brief pause
        except Exception as e:
            driver.save_screenshot("assign_button_error_final.png")
            logger.error(f"Failed to click 'Assign to Class': {e}", extra={'activity': 'Spelling Bee', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
            raise # Critical step, re-raise

    except Exception as e:
        driver.save_screenshot("spelling_bee_full_error.png")
        logger.error(f"Critical error during Spelling Bee assignment: {e}", extra={'activity': 'Spelling Bee', 'status': 'critical_failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    """
    Main function to initialize the browser, perform login,
    and create the Spelling Bee assignment.
    """
    driver = None
    try:
        # Initialize Chrome driver using WebDriverManager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window() # Maximize browser window for better visibility

        email = "ibadt@gmail.com"
        password = "ibad1234"

        login(driver, email, password)
        logger.info("--- Starting Spelling Bee Assignment Automation ---", extra={'activity': 'Main', 'status': 'started'})
        create_spelling_bee_assignment(driver)
        logger.info("Automation script finished successfully.", extra={'activity': 'Main', 'status': 'completed'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(3) # Give user time to see the final state
            driver.quit() # Close the browser

if __name__ == "__main__":
    main()