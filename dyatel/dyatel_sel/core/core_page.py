from logging import info

from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from dyatel.dyatel_sel.core.core_driver import CoreDriver
from dyatel.dyatel_sel.core.core_element import CoreElement
from dyatel.dyatel_sel.utils import get_locator_type, get_legacy_selector
from dyatel.internal_utils import get_child_elements


class CorePage:
    def __init__(self, locator, locator_type=None, name=None):
        self.driver = CoreDriver.driver
        self.driver_wrapper = CoreDriver(self.driver)
        self.url = getattr(self, 'url', '')

        if isinstance(self.driver, AppiumWebDriver):
            self.locator, self.locator_type = get_legacy_selector(locator, get_locator_type(locator))
        else:
            self.locator = locator
            self.locator_type = locator_type if locator_type else get_locator_type(locator)
        self.name = name if name else self.locator

        self.page_elements = get_child_elements(self, CoreElement)

        for el in self.page_elements:  # required for CoreElement
            if not el.driver:
                el.__init__(locator=el.locator, locator_type=el.locator_type, name=el.name, parent=el.parent)

    def reload_page(self, wait_page_load=True):
        """
        Reload current page

        :param wait_page_load: wait until anchor will be element loaded
        :return: self
        """
        info(f'Reload {self.name} page')
        self.driver_wrapper.refresh()
        if wait_page_load:
            self.wait_page_loaded()
        return self

    def open_page(self, url=''):
        """
        Open page with given url or use url from page class f url isn't given

        :param url: url for navigation
        :return: self
        """
        url = self.url if not url else url
        if not self.is_page_opened():
            self.driver_wrapper.get(url)
            self.wait_page_loaded()
        return self

    def wait_page_loaded(self, silent=False):
        """
        Wait until page loaded

        :param silent: erase log
        :return: self
        """
        if not silent:
            info(f'Wait until page "{self.name}" loaded')
        wait = WebDriverWait(self.driver, 10)
        wait.until(ec.visibility_of_element_located((self.locator_type, self.locator)))
        return self

    def is_page_opened(self):
        """
        Check is current page opened or not

        :return: self
        """
        if self.url:
            return self.driver_wrapper.current_url == self.url
        else:
            page_anchor = CoreElement(locator=self.locator, locator_type=self.locator_type, name=self.name)
            return page_anchor.is_displayed()
