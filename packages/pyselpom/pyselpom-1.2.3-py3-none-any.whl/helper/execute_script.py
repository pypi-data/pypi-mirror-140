import time

from selenium import webdriver

url = 'http://suninjuly.github.io/selects1.html'
browser = webdriver.Chrome()

try:
    browser.get(url)

    # browser.execute_script("alert('Robots at work');")
    # browser.execute_script("document.title='Script executing';")
    browser.execute_script("document.title='Script executing';alert('Robots at work');")
finally:
    time.sleep(5)
    browser.quit()
