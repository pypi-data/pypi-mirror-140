import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_addoption(parser):
    parser.addoption('--language', action='store', default='en', help='Specify language param.')
    parser.addoption('--browser_name', action='store', default='chrome', help='Choose browser: chrome or firefox')


@pytest.fixture
def driver(request) -> webdriver:
    user_language = request.config.getoption('language')
    browser_name = request.config.getoption('browser_name')

    if browser_name == 'chrome':
        print('\nStart chrome browser for test...')
        options = Options()
        options.add_experimental_option('prefs', {'intl.accept_languages': user_language})
        browser = webdriver.Chrome(options=options)
    elif browser_name == 'firefox':
        print('\nStart firefox browser for test...')
        fp = webdriver.FirefoxProfile()
        fp.set_preference('intl.accept_languages', user_language)
        browser = webdriver.Firefox(firefox_profile=fp)
    else:
        raise pytest.UsageError('--browser_name should be chrome or firefox')

    yield browser

    browser.quit()
