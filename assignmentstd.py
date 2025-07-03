import logging
import time
import traceback
import random
from pythonjsonlogger import jsonlogger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
logger = logging.getLogger("StudentAssignmentDashboard")
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)
logger.addHandler(stream_handler)

BASE_URL = "https://seeqlo-dev.vercel.app/login"

def login(driver, email, password):
    try:
        logger.info("Starting login process.", extra={'activity': 'Login', 'step': 'init'})
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 20)
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
        # Wait for nav/sidebar or dashboard to appear
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav"))
        )
        logger.info("Successfully logged in.", extra={'activity': 'Login', 'status': 'success'})
    except Exception as e:
        driver.save_screenshot("selenium_login_error.png")
        logger.error(f"Login failed: {str(e)}", extra={'activity': 'Login', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def go_to_dashboard(driver):
    wait = WebDriverWait(driver, 15)
    try:
        logger.info("Ensuring Dashboard tab is selected...", extra={'activity': 'Dashboard', 'step': 'ensure_dashboard'})
        # Try to click Dashboard tab if not already there
        try:
            dashboard_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Dashboard')]"))
            )
            driver.execute_script("arguments[0].click();", dashboard_tab)
            logger.info("Clicked on Dashboard tab.", extra={'activity': 'Dashboard', 'step': 'dashboard_tab_clicked'})
            time.sleep(2)
        except Exception:
            logger.info("Dashboard tab not found or already on Dashboard.", extra={'activity': 'Dashboard', 'step': 'dashboard_tab_not_found'})
    except Exception as e:
        logger.error(f"Error ensuring Dashboard: {str(e)}", extra={'activity': 'Dashboard', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def interact_with_pending_homework(driver):
    wait = WebDriverWait(driver, 20)
    try:
        logger.info("Looking for Pending Homework section...", extra={'activity': 'PendingHomework', 'step': 'find_section'})
        pending_section = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Pending Homework')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(false);", pending_section)
        logger.info("Scrolled to Pending Homework section.", extra={'activity': 'PendingHomework', 'step': 'scrolled'})
        time.sleep(1)
        logger.info("Looking for top assignment card...", extra={'activity': 'PendingHomework', 'step': 'find_assignment'})
        assignment_card = wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//h4[contains(text(), 'Math')]/parent::*)[1]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", assignment_card)
        time.sleep(1)
        assignment_card.click()
        logger.info("Clicked on the top pending assignment card.", extra={'activity': 'PendingHomework', 'step': 'assignment_clicked'})
        time.sleep(2)

        # --- Robust loop for all question types ---
        while True:
            handled = False
            # Try MCQ
            try:
                mcq_options = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'group') and .//span] | //label[contains(., '0.25') or contains(., '0.50') or contains(., '0.75') or contains(., '1.00')] | //input[@type='radio']/parent::label | //div[contains(@class, 'option-card')] | //button[contains(@class, 'mcq-option')] | //div[contains(@class, 'question-option')]"))
                )
                clickable_mcqs = [opt for opt in mcq_options if opt.is_displayed() and opt.is_enabled()]
                if clickable_mcqs:
                    selected_option = random.choice(clickable_mcqs)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_option)
                    time.sleep(0.5)
                    try:
                        if selected_option.tag_name.lower() == 'label':
                            try:
                                input_elem = selected_option.find_element(By.TAG_NAME, 'input')
                                input_elem.click()
                            except Exception:
                                selected_option.click()
                        elif selected_option.tag_name.lower() == 'div' and 'group' in selected_option.get_attribute('class'):
                            selected_option.click()
                        else:
                            selected_option.click()
                        logger.info("Answered MCQ.", extra={'activity': 'MCQ'})
                        handled = True
                    except Exception as e:
                        logger.warning(f"Failed to click MCQ option: {e}", extra={'activity': 'MCQ', 'step': 'option_click_error'})
            except Exception:
                pass
            # Try True/False
            if not handled:
                try:
                    tf_options = wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'group') and .//span] | //label[contains(., 'True') or contains(., 'False')] | //input[@type='radio']/parent::label | //button[contains(., 'True')] | //button[contains(., 'False')]"))
                    )
                    clickable_tf = [opt for opt in tf_options if opt.is_displayed() and opt.is_enabled()]
                    if clickable_tf:
                        selected_tf = random.choice(clickable_tf)
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_tf)
                        time.sleep(0.5)
                        try:
                            if selected_tf.tag_name.lower() == 'label':
                                try:
                                    input_elem = selected_tf.find_element(By.TAG_NAME, 'input')
                                    input_elem.click()
                                except Exception:
                                    selected_tf.click()
                            elif selected_tf.tag_name.lower() == 'div' and 'group' in selected_tf.get_attribute('class'):
                                selected_tf.click()
                            else:
                                selected_tf.click()
                            logger.info("Answered True/False.", extra={'activity': 'TrueFalse'})
                            handled = True
                        except Exception as e:
                            logger.warning(f"Failed to click True/False option: {e}", extra={'activity': 'TrueFalse', 'step': 'option_click_error'})
                except Exception:
                    pass
            # Try Match the Following
            if not handled:
                try:
                    dropdowns = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//select")))
                    for idx, dropdown in enumerate(dropdowns):
                        options = dropdown.find_elements(By.TAG_NAME, "option")
                        if len(options) > 1:
                            options[1].click()
                    logger.info("Answered Match the Following.", extra={'activity': 'Match'})
                    handled = True
                except Exception:
                    pass
            # Try Fill in the Blank
            if not handled:
                try:
                    textboxes = []
                    try:
                        textboxes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//textarea")))
                    except Exception:
                        textboxes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='text' or @type='search']")))
                    for idx, textbox in enumerate(textboxes):
                        textbox.clear()
                        textbox.send_keys(f"i am bot {123+idx}")
                    logger.info("Answered Fill in the Blank.", extra={'activity': 'FillBlank'})
                    handled = True
                except Exception:
                    pass
            # Look for Next or Submit Assignment button
            try:
                next_or_submit = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Next') or contains(., 'Submit Assignment')]"))
                )
                if 'Submit Assignment' in next_or_submit.text:
                    next_or_submit.click()
                    logger.info("Clicked Submit Assignment.", extra={'activity': 'Submit'})
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        logger.info("Accepted submit confirmation alert.", extra={'activity': 'Submit'})
                    except Exception:
                        pass
                    break
                elif next_or_submit.is_enabled():
                    next_or_submit.click()
                    logger.info("Clicked Next.", extra={'activity': 'Next'})
                    time.sleep(2)
                else:
                    logger.info("Next button is disabled. Ending loop.", extra={'activity': 'Next'})
                    break
            except Exception:
                logger.info("No Next or Submit Assignment button found. Ending loop.", extra={'activity': 'Next'})
                break
        # After the main question loop, always try to submit if possible
        try:
            submit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Submit Assignment')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            time.sleep(0.5)
            submit_btn.click()
            logger.info("Clicked 'Submit Assignment' button at the end.", extra={'activity': 'Submit', 'step': 'submit_clicked'})
            time.sleep(2)
            # Handle confirmation alert
            try:
                alert = driver.switch_to.alert
                alert.accept()
                logger.info("Accepted the submit confirmation alert.", extra={'activity': 'Submit', 'step': 'alert_accepted'})
                time.sleep(2)
            except Exception as e:
                logger.warning(f"No alert appeared or could not accept alert: {e}", extra={'activity': 'Submit', 'step': 'alert_not_found'})
        except Exception as e:
            logger.warning(f"Could not find or click 'Submit Assignment' button at the end: {e}", extra={'activity': 'Submit', 'step': 'submit_not_found'})
    except Exception as e:
        driver.save_screenshot("selenium_pending_homework_error.png")
        logger.error(f"Error interacting with Pending Homework: {str(e)}", extra={'activity': 'PendingHomework', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    driver = None
    try:
        logger.info("--- Starting Student Assignment Dashboard Automation ---", extra={'activity': 'Main', 'status': 'started'})
        driver = webdriver.Chrome()
        driver.maximize_window()
        email = "xyz@gmail.com"
        password = "hadi123"
        login(driver, email, password)
        go_to_dashboard(driver)
        interact_with_pending_homework(driver)
        logger.info("Student assignment interaction completed.", extra={'activity': 'Main', 'status': 'completed'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(5)  # Wait a few seconds before quitting to allow user to see final state
            time.sleep(2)
            driver.quit()

if __name__ == "__main__":
    main()
