from datetime import datetime
import os
import time
import allure
from webdriver_manager.chrome import ChromeDriverManager
from allure import attachment_type
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

class ChromeDriverSetup:
    
    def get_chrome_driver():
        options = Options()
        options.add_argument("start-maximized")  # open Browser in maximized mode
        options.add_argument("disable-infobars")  # disabling infobars
        options.add_argument("--disable-gpu")  # applicable to windows os only
        options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--headless") #starting headless mode
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        return driver
    
    def take_screenshot(driver):
        time.sleep(1)
        fileprefix = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0].strip('[]')
        now = datetime.now()
        print("now =", now)
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        file_name = f'{dt_string}.png'.replace("/","_").replace("::","__")
        image_path= f"{fileprefix}{file_name}"
        allure.attach(driver.get_screenshot_as_png(),name=image_path,attachment_type=attachment_type.PNG)
