from selenium import webdriver

browser = webdriver.Chrome()


# Prompt
prompt = browser.switch_to.alert
prompt.send_keys("My answer")
prompt.accept()


# Confirm
confirm = browser.switch_to.alert
confirm.accept()  # confirm.dismiss()

# Alerts
alert = browser.switch_to.alert
alert.accept()
alert_text = alert.text
