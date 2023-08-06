import math
import time

from selenium import webdriver

url = 'http://suninjuly.github.io/get_attribute.html'
browser = webdriver.Chrome()


def calc(x):
    return str(math.log(abs(12 * math.sin(int(x)))))


try:
    browser.get(url)

    value_element = browser.find_element_by_id('treasure').get_attribute('valuex')

    y = calc(value_element)

    answer = browser.find_element_by_id('answer').send_keys(y)
    robot_chk = browser.find_element_by_id('robotCheckbox').click()
    robot_radio = browser.find_element_by_id('robotsRule')
    robot_radio.click()
    print('robot:', robot_radio.get_attribute('checked'))

    human_radio = browser.find_element_by_id('peopleRule')
    print('people:', human_radio.get_attribute('checked'))

    submit = browser.find_element_by_tag_name('button').submit()

    # assert 'Congratulations! You have successfully registered!' == welcome_text

finally:
    time.sleep(5)
    browser.quit()
