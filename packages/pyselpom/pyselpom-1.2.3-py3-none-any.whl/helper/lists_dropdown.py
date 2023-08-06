import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select

url = 'http://suninjuly.github.io/selects1.html'
browser = webdriver.Chrome()

try:
    browser.get(url)

    # browser.execute_script("alert('Robots at work');")
    browser.execute_script("document.title='Script executing';")
    browser.execute_script("document.title='Script executing';alert('Robots at work');")

    time.sleep(5)

    num1 = browser.find_element_by_id('num1').text
    num2 = browser.find_element_by_id('num2').text
    result = int(num1) + int(num2)
    print(result)

    select = Select(browser.find_element_by_tag_name('select'))
    select.select_by_value(str(result))
    browser.find_element_by_tag_name('button').submit()

finally:
    time.sleep(15)
    browser.quit()
