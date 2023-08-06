import math
import time

from selenium import webdriver

url = 'http://suninjuly.github.io/redirect_accept.html'
browser = webdriver.Chrome()


def calc(x):
    return str(math.log(abs(12 * math.sin(int(x)))))


try:
    browser.get(url)
    browser.find_element_by_css_selector('.btn.btn-primary').click()

    browser.switch_to.window(browser.window_handles[1])

    value_element = int(browser.find_element_by_id('input_value').text)

    y = calc(value_element)

    browser.find_element_by_id('answer').send_keys(y)


    browser.find_element_by_tag_name('button').submit()

    # assert 'Congratulations! You have successfully registered!' == welcome_text

finally:
    time.sleep(5)
    browser.quit()
