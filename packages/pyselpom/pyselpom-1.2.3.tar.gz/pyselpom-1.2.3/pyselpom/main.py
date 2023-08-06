__author__ = 'Andrey Komissarov'
__email__ = 'a.komisssarov@gmail.com'
__date__ = '2022'

import inspect
import urllib.parse as urlparse
from functools import wraps

import allure
from allure_commons.types import AttachmentType
from plogger import logger
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver as FFDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# By.ID
# By.CSS_SELECTOR
# By.XPATH
# By.NAME
# By.TAG_NAME
# By.CLASS_NAME
# By.LINK_TEXT
# By.PARTIAL_LINK_TEXT

def log_params(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Log method name ad specific parameters"""

        logger_name = f'{func.__qualname__.replace(".", "->")}({func.__code__.co_firstlineno})'
        logger_ = logger(logger_name)

        signature = inspect.signature(func)
        signature_log = {
            key: value.default
            for key, value in signature.parameters.items()
            if value.default is not inspect.Parameter.empty
        }

        log_info = f'Signature: {signature_log}'

        # Log positional params. Number == number of args -1 (-self)
        if number := len(args) > 1:
            args_ = ", ".join(map(str, args[1:]))
            log_info += f' | {len(args) - 1} positional param(s): "{args_}"'

        # Log named arguments
        kwargs_ = locals()["kwargs"]
        if kwargs_:
            log_info += f' | {len(kwargs_)} named param(s): {kwargs_}'
        logger_.info(log_info)

        return func(*args, **kwargs)

    return wrapper


class BasePage:
    """Base Page with common methods to work with web elements"""

    URL_PATTERN = None

    def __init__(self,
                 driver: ChromeDriver,
                 url: str = None,
                 implicit_timeout: int = 0,
                 start_opened: bool = False,
                 maximize: bool = True):

        if driver.name == 'firefox':
            self.driver: FFDriver = driver
        elif driver.name == 'chrome':
            self.driver: ChromeDriver = driver

        self.url: str = url

        # Use implicit waiting if specified
        if implicit_timeout:
            self.driver.implicitly_wait(implicit_timeout)

        self.logger = logger(self.__class__.__name__)

        if start_opened:  # Open base page during initialisation if specified
            self.open(maximize=maximize)

    @property
    def seed_url(self) -> str:
        """Create URL.

        If URL_PATTERN specified, you can use base_url without domain.

        Usage:
        URL_PATTERN = https://www.google.com
        BasePage(driver, url='search')
        Result: https://www.google.com/search

        :return: URL
        """

        return urlparse.urljoin(self.URL_PATTERN, self.url) if self.URL_PATTERN is not None else self.url

    def _waiter(self, timeout: int) -> WebDriverWait:
        """

        :param timeout:
        :return:
        """

        return WebDriverWait(self.driver, timeout)

    def open(self, maximize: bool = False):
        """Start browser and navigate to url specified in constructor.

        :param maximize: Maximize opened browser
        :return:
        """

        url = self.seed_url if self.seed_url else self.url
        driver = self.driver.get(url)

        if maximize:
            self.driver.maximize_window()
        self.logger.info(f'Open {url}')

        return driver

    def quit(self):
        return self.driver.quit()

    def find_element(self, by: By, locator: str, timeout: int = 5) -> WebElement:
        """Default high-level find element with waiting method

        :param by:
        :param locator:
        :param timeout:
        :return:
        """

        self.logger.info(f'Find element <{locator}> by <{by}> during {timeout} sec.')

        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, locator)), message=self._message(by, locator))

    def find_elements(self, by: By, locator: str, timeout: int = 5) -> list[WebElement]:
        """Default high-level find many elements with waiting method

        :param by:
        :param locator:
        :param timeout:
        :return:
        """

        self.logger.info(f'Find element <{locator}> by <{by}> during {timeout} sec.')

        wait = self._waiter(timeout)
        return wait.until(EC.presence_of_all_elements_located((by, locator)), message=self._message(by, locator))

    def is_visible(self, by: By, locator: str, timeout: int = 5) -> bool:
        """Find element and verify it is visible

        :param by:
        :param locator:
        :param timeout:
        :return:
        """

        wait = self._waiter(timeout)
        try:
            wait.until(EC.visibility_of_element_located((by, locator)), message=self._message(by, locator))
        except TimeoutException:
            return False
        return True

    def is_not_visible(self, by: By, locator: str, timeout: int = 5) -> bool:
        """Find element and verify it is hidden

        :param by:
        :param locator:
        :param timeout:
        :return:
        """

        wait = self._waiter(timeout)
        elem = wait.until(EC.invisibility_of_element_located((by, locator)), message=self._message(by, locator))

        return elem.is_displayed()

    def is_clickable(self, by: By, locator: str, timeout: int = 5) -> bool:
        """Find element and verify it is clickable

        :param by:
        :param locator:
        :param timeout:
        :return:
        """

        wait = self._waiter(timeout)
        try:
            wait.until(EC.element_to_be_clickable((by, locator)), message=self._message(by, locator))
        except TimeoutException:
            return False
        return True

    @staticmethod
    def _message(by: By, locator: str):
        return f'Element not found: {by, locator}'

    def is_element_present(self, by: By, locator: str, timeout: int = 1) -> bool:
        """Verify element exists on page

        :param by:
        :param locator:
        :param timeout:
        :return:
        """

        try:
            self.find_element(by, locator, timeout=timeout)
        except NoSuchElementException:
            return False
        return True

    def is_not_element_present(self, by: By, locator: str, timeout: int = 4) -> bool:
        """Try to find element and verify it absent on page

        :param by:
        :param locator:
        :param timeout:
        :return:
        """

        try:
            self.find_element(by, locator, timeout=timeout)
            # WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, locator)))
        except TimeoutException:
            return True
        return False

    def is_disappeared(self, by: By, locator: str, timeout: int = 4) -> bool:
        """Find element and verify it disappeared

        :param by:
        :param locator:
        :param timeout:
        :return:
        """

        try:
            wait = WebDriverWait(self.driver, timeout, ignored_exceptions=TimeoutException)
            wait.until_not(EC.presence_of_element_located((by, locator)))
        except TimeoutException:
            return False
        return True

    def get_value(self, by: By, locator: str, attr_name: str):
        """Find element and get attribute. Gets the given attribute or property of the element.

        :param by:
        :param locator:
        :param attr_name:
        :return:
        """

        return self.find_element(by, locator).get_attribute(attr_name)  # TODO necessary to verify method

    def set_value(self, text: str, by: By, locator: str):
        """Find input element and fill with the specific text

        :param text:
        :param by:
        :param locator:
        :return:
        """

        elem = self.find_element(by, locator)
        elem.click()
        elem.clear()
        elem.send_keys(text)

    def get_text(self, by: By, locator: str) -> str:
        """Find element and get element's text

        :param by:
        :param locator:
        :return:
        """

        return self.find_element(by, locator).text

    def clear(self, by: By, locator: str):
        """Fine input element and clear it

        :param by:
        :param locator:
        :return:
        """

        return self.find_element(by, locator).clear()

    def press(self, by: By, locator: str):
        """Find element (button) and press it

        :param by:
        :param locator:
        :return:
        """

        return self.find_element(by, locator).click()

    def get_screen_shot(self, name: str = ''):
        """Attach screenshot to Allure report

        :param name:
        :return:
        """

        return allure.attach(self.driver.get_screenshot_as_png(), name=name, attachment_type=AttachmentType.PNG)

    def execute_script(self, script, *args):
        """Execute JS script

        "alert('Robots at work');"
        "document.title='Script executing';"
        "document.title='Script executing';alert('Robots at work');"

        :param script:
        :param args:
        :return:
        """

        return self.driver.execute_script(script, *args)

    def is_alert_present(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
        except NoAlertPresentException:
            return False
        return True
