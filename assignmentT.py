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
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, ElementNotInteractableException

# Logger setup (assuming this part is correct and doesn't need changes for the current problem)
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
logger = logging.getLogger("TeacherAssignment")
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)
logger.addHandler(stream_handler)

BASE_URL = "https://seeqlo-dev.vercel.app"

def login(driver, email, password):
    try:
        logger.info("Starting login process.", extra={'activity': 'Login', 'step': 'init'})
        driver.get(BASE_URL + "/login")
        wait = WebDriverWait(driver, 20)
        logger.info("Entering email...", extra={'activity': 'Login', 'step': 'entering_email'})
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@placeholder, 'example.com')]") ))
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

def navigate_to_my_desk(driver):
    wait = WebDriverWait(driver, 20)
    try:
        logger.info("Navigating to 'My Desk'...", extra={'activity': 'Assignment', 'step': 'navigate_my_desk'})
        my_desk_span = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'My Desk')]")
        ))
        my_desk_span.click()
        logger.info("Pressed 'My Desk' navigation link.", extra={'activity': 'Assignment', 'step': 'my_desk_clicked'})
    except Exception as e:
        driver.save_screenshot("selenium_my_desk_error.png")
        logger.error(f"Navigation to My Desk error: {e}", extra={'activity': 'Assignment', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def fill_assignment_details(driver, assignment_type):
    """
    Fills the details form for a given assignment type ('Multiple Choice' or 'True/False' ).
    """
    wait = WebDriverWait(driver, 20)
    log_extra = {'activity': f'Fill{assignment_type.replace("/", "")}Details'}
    try:
        logger.info(f"Proceeding to fill details for {assignment_type} assignment.", extra=log_extra)
        # --- Continue to Details Page ---
        continue_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue to Assignment Details')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
        time.sleep(1)
        continue_btn.click()
        logger.info("'Continue to Assignment Details' button clicked.", extra=log_extra)
        # --- Assign to Classes ---
        class_dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Choose classes...']]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", class_dropdown_btn)
        time.sleep(1)
        class_dropdown_btn.click()
        logger.info("Clicked 'Choose classes...' dropdown.", extra=log_extra)
        time.sleep(2)
        scrollable_container = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'overflow-y-auto') or contains(@class, 'scrollbar') or contains(@class, 'max-h')][descendant::*[contains(text(), 'math grade 5')]]")))
        found = False
        for _ in range(5):
            try:
                math_grade_5_option = scrollable_container.find_element(By.XPATH, ".//*[contains(text(), 'math grade 5') and (self::li or self::div)]")
                if math_grade_5_option.is_displayed():
                    found = True
                    break
            except Exception:
                pass
            driver.execute_script("arguments[0].scrollTop += 100;", scrollable_container)
            time.sleep(0.3)
        math_grade_5_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'math grade 5') and (self::li or self::div)]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", math_grade_5_option)
        time.sleep(0.5)
        math_grade_5_option.click()
        logger.info("Selected 'math grade 5' from dropdown.", extra=log_extra)
        # Grade
        grade_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//select[./option[contains(text(), "Grade")]]')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", grade_dropdown)
        time.sleep(1)
        select_grade = Select(grade_dropdown)
        try:
            select_grade.select_by_visible_text("Grade 7")
        except Exception:
            for opt in select_grade.options:
                if '7' in opt.text:
                    select_grade.select_by_visible_text(opt.text)
                    break
        # Subject
        subject_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '(//label[contains(text(), "Subject")]/following-sibling::select | //select)[2]')))
        for _ in range(10):
            if subject_dropdown.is_enabled() and len(subject_dropdown.find_elements(By.TAG_NAME, 'option')) > 1:
                break
            time.sleep(0.5)
        select_subject = Select(subject_dropdown)
        try:
            select_subject.select_by_visible_text("Mathematics")
        except Exception:
            for opt in select_subject.options:
                if 'Math' in opt.text:
                    select_subject.select_by_visible_text(opt.text)
                    break
        # Unit
        unit_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '(//label[contains(text(), "Unit")]/following-sibling::select | //select)[3]')))
        for _ in range(10):
            if unit_dropdown.is_enabled() and len(unit_dropdown.find_elements(By.TAG_NAME, 'option')) > 1:
                break
            time.sleep(0.5)
        select_unit = Select(unit_dropdown)
        try:
            select_unit.select_by_visible_text("Numbers")
        except Exception:
            for opt in select_unit.options:
                if 'Number' in opt.text:
                    select_unit.select_by_visible_text(opt.text)
                    break
        # Due date (set with JS)
        due_date_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='date']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", due_date_input)
        time.sleep(0.5)
        driver.execute_script("arguments[0].value = '2026-07-03';", due_date_input)
        # Scroll down
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(0.5)
        # Assignment description
        desc_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//textarea[contains(@placeholder, 'assignment instructions') or contains(@placeholder, 'context') or contains(@placeholder, 'description') or contains(@placeholder, 'Provide')]")))
        desc_input.clear()
        desc_input.send_keys("sets")
        # Generate with AI
        gen_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'generate') and contains(., 'AI')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gen_btn)
        time.sleep(1)
        gen_btn.click()
        time.sleep(20)
        # Send Homework
        send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Send Homework')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", send_btn)
        time.sleep(1)
        send_btn.click()
        time.sleep(10)
    except Exception as e:
        driver.save_screenshot(f"selenium_{assignment_type.replace('/', '').lower()}_details_error.png")
        logger.error(f"Error filling {assignment_type} details: {e}", extra={**log_extra, 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def create_assignment(driver, assignment_type):
    # Reduce timeout for question type selection to 1 second
    wait = WebDriverWait(driver, 20)
    try:
        logger.info(f"Clicking 'Create Assignment' button for {assignment_type}...", extra={'activity': 'Assignment', 'step': 'click_create_assignment'})
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Assignment')]")))
        create_btn.click()
        logger.info("'Create Assignment' button clicked.", extra={'activity': 'Assignment', 'step': 'create_assignment_clicked'})
        time.sleep(2)
        logger.info(f"Selecting '{assignment_type}' assignment type...", extra={'activity': 'Assignment', 'step': f'select_{assignment_type.replace("/", "").lower()}'} )
        # Use a short wait for question type selection
        short_wait = WebDriverWait(driver, 1)
        try:
            type_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{assignment_type}') and contains(@class, 'cursor-pointer')]")))
        except TimeoutException:
            type_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{assignment_type}')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", type_btn)
        time.sleep(1)
        type_btn.click()
        logger.info(f"'{assignment_type}' assignment type selected.", extra={'activity': 'Assignment', 'step': f'{assignment_type.replace("/", "").lower()}_selected'})
        time.sleep(2)
        fill_assignment_details(driver, assignment_type)
    except Exception as e:
        driver.save_screenshot(f"selenium_assignment_{assignment_type.replace('/', '').lower()}_error.png")
        logger.error(f"Assignment creation error for {assignment_type}: {e}", extra={'activity': 'Assignment', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def select_all_assignment_types(driver):
    """
    Routine to select the first available assignment type from the list, then fill and send the assignment (same as per-type routine).
    """
    wait = WebDriverWait(driver, 5)
    assignment_types = [
        "Multiple Choice",
        "True/False",
        "Fill in the Blank",
        "Matching",
        "Short Answer"
    ]
    logger.info("Selecting all assignment types in one routine...", extra={'activity': 'Assignment', 'step': 'select_all_types'})
    try:
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Assignment')]")))
        create_btn.click()
        logger.info("'Create Assignment' button clicked for all types.", extra={'activity': 'Assignment', 'step': 'create_assignment_clicked_all'})
        time.sleep(2)
        selected_type = None
        for assignment_type in assignment_types:
            try:
                short_wait = WebDriverWait(driver, 1)
                try:
                    type_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{assignment_type}') and contains(@class, 'cursor-pointer')]")))
                except TimeoutException:
                    type_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{assignment_type}')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", type_btn)
                time.sleep(0.5)
                type_btn.click()
                logger.info(f"'{assignment_type}' selected in all-types routine.", extra={'activity': 'Assignment', 'step': f'select_all_{assignment_type.replace("/", "").lower()}'})
                selected_type = assignment_type
                break  # Only select the first available type and proceed
            except Exception as e:
                logger.warning(f"Could not select {assignment_type} in all-types routine: {e}", extra={'activity': 'Assignment', 'step': f'select_all_{assignment_type.replace("/", "").lower()}', 'error_message': str(e)})
        if selected_type:
            fill_assignment_details(driver, selected_type)
        else:
            logger.error("No assignment type could be selected in all-types routine.", extra={'activity': 'Assignment', 'step': 'select_all_types_failed'})
    except Exception as e:
        driver.save_screenshot("selenium_select_all_types_error.png")
        logger.error(f"Error in select_all_assignment_types: {e}", extra={'activity': 'Assignment', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def create_assignment_with_all_types(driver):
    """
    Create an assignment where all question types are selected (if UI allows multi-select), and fill/send as normal.
    This version is optimized for speed: minimal sleep, short waits, and skips unnecessary delays.
    """
    wait = WebDriverWait(driver, 10)
    assignment_types = [
        "Multiple Choice",
        "True/False",
        "Fill in the Blank",
        "Matching",
        "Short Answer"
    ]
    try:
        logger.info("Clicking 'Create Assignment' button for all question types...", extra={'activity': 'Assignment', 'step': 'click_create_assignment_all_types'})
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Assignment')]")))
        create_btn.click()
        logger.info("'Create Assignment' button clicked for all types.", extra={'activity': 'Assignment', 'step': 'create_assignment_clicked_all_types'})
        # Try to select all types (multi-select UI)
        for assignment_type in assignment_types:
            try:
                short_wait = WebDriverWait(driver, 0.5)
                try:
                    type_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{assignment_type}') and contains(@class, 'cursor-pointer')]")))
                except TimeoutException:
                    type_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{assignment_type}')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", type_btn)
                type_btn.click()
                logger.info(f"'{assignment_type}' selected in all-types assignment.", extra={'activity': 'Assignment', 'step': f'select_all_{assignment_type.replace("/", "").lower()}_assignment'})
            except Exception as e:
                logger.warning(f"Could not select {assignment_type} in all-types assignment: {e}", extra={'activity': 'Assignment', 'step': f'select_all_{assignment_type.replace("/", "").lower()}_assignment', 'error_message': str(e)})
        # Continue to details and send assignment as normal, but minimize waits
        fill_assignment_details(driver, assignment_types[0])  # Use first type for logging/activity
    except Exception as e:
        driver.save_screenshot("selenium_assignment_all_types_error.png")
        logger.error(f"Assignment creation error for all types: {e}", extra={'activity': 'Assignment', 'status': 'failure', 'error_message': str(e), 'traceback': traceback.format_exc()})
        raise

def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        email = "ibadt@gmail.com"
        password = "ibad1234"
        login(driver, email, password)
        navigate_to_my_desk(driver)
        # Create assignment with all question types selected
        create_assignment_with_all_types(driver)
        # Then run each type separately
        for assignment_type in [
            "Multiple Choice",
            "True/False",
            "Fill in the Blank",
            "Matching",
            "Short Answer"
        ]:
            create_assignment(driver, assignment_type)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()