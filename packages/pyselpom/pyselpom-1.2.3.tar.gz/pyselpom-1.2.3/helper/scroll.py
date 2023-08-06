import math
import time

from selenium import webdriver

url = 'http://suninjuly.github.io/execute_script.html'
browser = webdriver.Chrome()

try:
    browser.get(url)
    browser.maximize_window()
    value = int(browser.find_element_by_id('input_value').text)

    result = math.log(abs(12*math.sin(value)))
    print(result)

    button = browser.find_element_by_tag_name('button')
    browser.execute_script('window.scrollBy(0, 100)')
    # browser.execute_script('arguments[0].scrollIntoView(true);', button)
    answer = browser.find_element_by_id('answer').send_keys(result)
    browser.find_element_by_id('robotCheckbox').click()

    robot_radio = browser.find_element_by_id('robotsRule')
    robot_radio.click()



    button.click()
finally:
    time.sleep(5)
    browser.quit()
