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
logger = logging.getLogger("TeacherActivePassive")
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)
logger.addHandler(stream_handler)

BASE_URL = "https://seeqlo-dev.vercel.app"

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

def start_parts_of_speech_assignment(driver):
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
        logger.info("Looking for 'parts of speech' activity in Pending Activities...", extra={'activity': 'StartActivity', 'step': 'find_parts_of_speech'})
        start_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Start Activity') or contains(text(), 'Start')]")
        found = False
        for btn in start_buttons:
            try:
                card = btn.find_element(By.XPATH, "ancestor::div[contains(@class, 'flex')][1]")
                if 'parts of speech' in card.text.lower():
                    driver.execute_script("arguments[0].scrollIntoView(false);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    logger.info("Clicked Start Activity for 'parts of speech'.", extra={'activity': 'StartActivity', 'step': 'start_clicked'})
                    found = True
                    break
            except Exception as e:
                continue
        if not found:
            logger.warning("No 'parts of speech' activity found in Pending Activities.", extra={'activity': 'StartActivity', 'status': 'not_found'})
        else:
            logger.info("Activity started.", extra={'activity': 'StartActivity', 'status': 'started'})
            time.sleep(10)  # Wait for activity to load
            question_num = 1
            while True:
                try:
                    logger.info(f"Processing question {question_num}...", extra={'activity': 'StartActivity', 'step': f'question_{question_num}'})
                    # Check for Try Again button first
                    try_again_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Try Again')]")
                    if try_again_btns:
                        logger.info("'Try Again' button appeared. Activity completed!", extra={'activity': 'StartActivity', 'status': 'completed'})
                        print('Activity completed!')
                        break
                    # Find yellow highlighted word
                    try:
                        highlighted = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@style, 'background-color') and contains(@style, 'yellow')]")))
                    except Exception:
                        try:
                            highlighted = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'yellow') or contains(@class, 'bg-yellow')]")))
                        except Exception:
                            logger.info("No more yellow highlighted word found. Assuming activity is complete.", extra={'activity': 'StartActivity', 'step': 'no_more_questions'})
                            break
                    logger.info("Found yellow highlighted word.", extra={'activity': 'StartActivity', 'step': f'highlighted_found_{question_num}'})
                    # Find the first answer box
                    answer_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dashed')][1]")))
                    from selenium.webdriver.common.action_chains import ActionChains
                    try:
                        actions = ActionChains(driver)
                        actions.click_and_hold(highlighted).move_to_element(answer_box).release().perform()
                        logger.info("Dragged highlighted word into answer box using ActionChains.", extra={'activity': 'StartActivity', 'step': f'dragged_{question_num}'})
                    except Exception as e:
                        logger.warning(f"ActionChains drag failed: {e}. Trying click method...", extra={'activity': 'StartActivity', 'step': f'drag_fallback_{question_num}'})
                        try:
                            highlighted.click()
                            time.sleep(0.5)
                            answer_box.click()
                            logger.info("Clicked highlighted word and answer box as fallback.", extra={'activity': 'StartActivity', 'step': f'clicked_fallback_{question_num}'})
                        except Exception as e2:
                            logger.error(f"Both drag and click fallback failed: {e2}", extra={'activity': 'StartActivity', 'status': 'failure'})
                            break
                    # Click Check Answer
                    try:
                        check_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Check Answer')]")))
                        check_btn.click()
                        logger.info("Clicked Check Answer.", extra={'activity': 'StartActivity', 'step': f'check_answer_{question_num}'})
                        time.sleep(2)
                    except Exception:
                        logger.info("No Check Answer button found. Assuming activity is complete.", extra={'activity': 'StartActivity', 'step': 'no_check_button'})
                        break
                    question_num += 1
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"Error during question loop: {e}", extra={'activity': 'StartActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
                    break
            logger.info("Completed all available questions.", extra={'activity': 'StartActivity', 'status': 'completed'})
        time.sleep(3)
    except Exception as e:
        driver.save_screenshot("activepassive_assignment_error.png")
        logger.error(f"Assignment error: {e}", extra={'activity': 'StartActivity', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    driver = None
    try:
        logger.info("--- Starting Teacher ActivePassive Automation ---", extra={'activity': 'Main', 'status': 'started'})
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = "https://seeqlo-dev.vercel.app/login"
        driver.get(url)
        logger.info(f"Navigated to {url}", extra={'activity': 'Main', 'step': 'navigation'})
        email = "xyz@gmail.com"
        password = "hadi123"
        login(driver, email, password)
        logger.info("Starting teacher active/passive activity...", extra={'activity': 'Main', 'status': 'activity_start'})
        start_parts_of_speech_assignment(driver)
        logger.info("Teacher activity completed successfully", extra={'activity': 'Main', 'status': 'activity_started'})
    except Exception as e:
        logger.error(f"Script stopped: {e}", extra={'activity': 'Main', 'status': 'script_stopped', 'error_message': str(e), 'traceback': traceback.format_exc()})
    finally:
        if driver:
            logger.info("Closing browser...", extra={'activity': 'Main', 'step': 'closing_browser'})
            time.sleep(2)
            driver.quit()

if __name__ == "__main__":
    main()
