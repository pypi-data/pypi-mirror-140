import os
import time

from selenium import webdriver

url = 'http://suninjuly.github.io/file_input.html'
browser = webdriver.Chrome()

try:
    browser.get(url)

    browser.find_element_by_name('firstname').send_keys('firstname')
    browser.find_element_by_name('lastname').send_keys('lastname')
    browser.find_element_by_name('email').send_keys('email')

    current_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(current_dir, 'file.txt')
    browser.find_element_by_name('file').send_keys(file_path)

    browser.find_element_by_css_selector('.btn.btn-primary').submit()

finally:
    time.sleep(5)
    browser.quit()
