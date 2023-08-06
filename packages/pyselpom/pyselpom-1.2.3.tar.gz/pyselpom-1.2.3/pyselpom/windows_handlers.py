from selenium.common.exceptions import NoAlertPresentException


class WindowsHandler:

    def __init__(self, driver):
        self._driver = driver

    def scroll(self):
        raise NotImplementedError

    def save_window_set(self):
        self._snapshot_of_handles = set(self._driver.window_handles)

    @property
    def new_window(self):
        new_handles = set(self._driver.window_handles)
        new_handles = new_handles - self._snapshot_of_handles

        return next(iter(new_handles))

    @property
    def active_window(self):
        self._active_window = self._driver.current_window_handle
        return self._active_window

    @property
    def handles(self):
        return self._driver.window_handles

    def switch_to_window(self, window_handle):
        self._driver.switch_to_window(window_handle)

    def switch_to_new_window(self):
        raise NotImplementedError

    def switch_to_parent_window(self):
        raise NotImplementedError

    def close_active_window(self):
        self._driver.close()
        self.drop_active_window()

    def drop_active_window(self):
        raise NotImplementedError

    def create_window(self):
        self.save_window_set()
        self._driver.execute_script("window.open('');")
        return self.new_window

    def is_alert_present(self):
        try:
            self.get_alert_text()
            return True
        except NoAlertPresentException:
            return False

    def is_new_window_present(self):
        return len(self._driver.window_handles) - len(self._snapshot_of_handles) > 0

    def accept_alert(self):
        self._driver.switch_to_alert().accept()

    def get_alert_text(self):
        return self._driver.switch_to_alert().text
