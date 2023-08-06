import time

from selenium import webdriver

url = 'http://suninjuly.github.io/registration2.html'
browser = webdriver.Chrome()

try:
    browser.get(url)

    main_class = '.first_block'
    input_name = browser.find_element_by_css_selector(f'{main_class} .first')
    input_name.send_keys('Ivan')
    input_surname = browser.find_element_by_css_selector(f'{main_class} .second')
    input_surname.send_keys('Petrov')
    input_mail = browser.find_element_by_css_selector(f'{main_class} .third')
    input_mail.send_keys('mail@smt.com')

    button = browser.find_element_by_xpath('//*[@type="submit"]').click()

    time.sleep(1)

    welcome_text_elt = browser.find_element_by_tag_name('h1')
    welcome_text = welcome_text_elt.text

    assert 'Congratulations! You have successfully registered!' == welcome_text

finally:
    browser.quit()
