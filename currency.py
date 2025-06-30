import logging
import time
import traceback
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AssignmentAutomation")

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
        logger.info("▶ Starting login process...")
        driver.get(BASE_URL + "/login")
        wait = WebDriverWait(driver, 20) # Increased timeout for login page load

        logger.info("✉ Entering email...")
        # Wait for the email input field to be present and visible
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@placeholder, 'example.com')]")))
        email_input.send_keys(email)
        logger.info("📧 Email entered.")

        logger.info("🔑 Entering password...")
        # Wait for the password input field to be present and visible
        password_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
        password_input.send_keys(password)
        logger.info("🔒 Password entered.")

        logger.info("-> Clicking login button...")
        # Wait for the login button to be clickable
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]")))
        login_btn.click()
        logger.info("✅ Login button clicked.")

        logger.info("🔐 Waiting for dashboard...")
        # Wait until the URL changes from login and a specific dashboard element is present
        wait.until(EC.url_changes(BASE_URL + "/login"))
        wait.until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space(.)='Welcome back, ibadt']")))
        logger.info("✅ Login successful. Dashboard loaded.")

    except Exception as e:
        driver.save_screenshot("selenium_login_error.png") # Capture screenshot on error
        logger.error(f"Login error: {e}")
        traceback.print_exc()
        raise # Re-raise the exception to stop the script on critical failure

def create_currency_activity_assignment(driver): # Renamed function for Currency Activity
    """
    Automates the creation of a Currency Activity assignment.

    Args:
        driver: Selenium WebDriver instance.
    """
    wait = WebDriverWait(driver, 20) # Increased timeout for activity creation steps

    try:
        logger.info("\n🖥️ Navigating to 'My Desk'...")
        my_desk_span = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'My Desk')]")
        ))
        my_desk_span.click()
        logger.info("✅ Automation script pressed 'My Desk' navigation link.")
        time.sleep(2) # Allow page to settle after navigation

        logger.info("\n💰 Clicking 'Currency Activity'...") # Updated log for Currency Activity
        currency_activity = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'cursor-pointer')]//div[contains(., 'Currency Activity')]") # Updated XPath for Currency Activity
        ))
        currency_activity.click()
        logger.info("✅ Automation script pressed 'Currency Activity'.")
        time.sleep(2) # Allow activity page to load completely

        logger.info("\n🔎 Selecting class 'math grade 5 (2 students)'...")
        # Wait for the class dropdown to be present and visible
        class_dropdown_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//select[contains(@class, "w-full") and (./option[contains(text(), "-- Select Class --")] or ./option[contains(text(), "math grade 5 (2 students)")])]')))
        class_dropdown = Select(class_dropdown_element)
        class_dropdown.select_by_visible_text("math grade 5 (2 students)")
        logger.info("🎓 Automation script chose 'math grade 5 (2 students)' class for Currency Activity.") # Updated log
        time.sleep(1) # Short pause after selection to allow UI updates

        # Scrolling logic for the main form container (if any elements below are hidden)
        logger.info("📜 Scrolling down the form to reveal hidden elements (if any)...")
        try:
            scrollable_form = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'space-y-3') and contains(@class, 'lg:overflow-y-auto')]")
            ))
            for _ in range(3): # Scroll by 200px, three times
                driver.execute_script("arguments[0].scrollTop += 200;", scrollable_form)
                time.sleep(0.5) # Small pause between scrolls
            logger.info("✅ Automation script scrolled down the form to reveal content.")
        except Exception as e:
            logger.warning(f"⚠️ Scroll of the main form content failed: {e}")
            driver.save_screenshot("scrolling_failed.png")


        logger.info("\n✨ Clicking 'Generate Content' button...")
        try:
            generate_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[./span[text()='Generate Content']]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", generate_btn)
            time.sleep(1)

            generate_btn.click()
            logger.info("✅ Automation script clicked 'Generate Content' button.")

            logger.info("⏳ Waiting 15 seconds for content generation by AI...")
            time.sleep(15) # Increased wait time for AI content generation

        except ElementClickInterceptedException as e:
            screenshot_path = "generate_button_intercepted.png"
            driver.save_screenshot(screenshot_path)
            logger.warning(f"Click on 'Generate Content' intercepted: {e}. Retrying with JS click.", extra={'screenshot': screenshot_path})
            driver.execute_script("arguments[0].click();", generate_btn)
            logger.info("✅ Automation script used JS to click 'Generate Content' after interception.")
            time.sleep(15)
        except Exception as e:
            driver.save_screenshot("generate_button_error.png")
            logger.error(f"❌ Failed to click 'Generate Content': {e}")
            traceback.print_exc()
            raise

        logger.info("\n🚀 Clicking 'Assign to Class' button...")
        try:
            assign_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Assign to Class')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", assign_btn)
            time.sleep(0.5)

            assign_btn.click()
            logger.info("✅ Automation script successfully assigned the activity to the class.")
            time.sleep(3)

        except ElementClickInterceptedException as e:
            screenshot_path = "assign_button_intercepted_final.png"
            driver.save_screenshot(screenshot_path)
            logger.warning(f"Click on 'Assign to Class' intercepted: {e}. Retrying with JS click.", extra={'screenshot': screenshot_path})
            driver.execute_script("arguments[0].click();", assign_btn)
            logger.info("✅ Automation script used JS to click 'Assign to Class' after interception.")
            time.sleep(3)
        except Exception as e:
            driver.save_screenshot("assign_button_error_final.png")
            logger.error(f"❌ Failed to click 'Assign to Class': {e}")
            traceback.print_exc()
            raise

    except Exception as e:
        driver.save_screenshot("currency_activity_full_error.png") # Updated screenshot name
        logger.error(f"❌ Critical error during Currency Activity assignment: {e}") # Updated error message
        traceback.print_exc()
        raise

def main():
    """
    Main function to initialize the browser, perform login,
    and create the Currency Activity assignment.
    """
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()

        email = "ibadt@gmail.com"
        password = "ibad1234"

        login(driver, email, password)
        logger.info("\n--- Starting Currency Activity Assignment Automation ---") # Updated log
        create_currency_activity_assignment(driver) # Updated function call
        logger.info("🎯 Automation script finished successfully.")
    except Exception as e:
        logger.error(f"💥 Script stopped: {e}")
        traceback.print_exc()
    finally:
        if driver:
            logger.info("👋 Closing browser...")
            time.sleep(3)
            driver.quit()

if __name__ == "__main__":
    main()
