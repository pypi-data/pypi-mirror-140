import math
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

url = 'http://suninjuly.github.io/explicit_wait2.html'
browser = webdriver.Chrome()


def calc(x):
    return str(math.log(abs(12 * math.sin(int(x)))))


try:
    browser.get(url)

    button = WebDriverWait(browser, 15).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.card-body #price'), '$100')
    )


    browser.find_element_by_css_selector('.btn.btn-primary').click()


    result = int(browser.find_element_by_id('input_value').text)
    value = calc(result)

    browser.find_element_by_id('answer').send_keys(value)

    browser.find_element_by_id('solve').submit()
    # assert 'Congratulations! You have successfully registered!' == welcome_text

finally:
    time.sleep(5)
    browser.quit()
