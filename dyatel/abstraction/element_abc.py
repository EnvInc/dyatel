from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Union, Any, List

from PIL.Image import Image
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from appium.webdriver.webelement import WebElement as AppiumWebElement
from playwright.sync_api import Locator as PlayWebElement

from dyatel.abstraction.mixin_abc import MixinABS
from dyatel.keyboard_keys import KeyboardKeys
from dyatel.utils.internal_utils import WAIT_EL


class ElementABS(ABC, MixinABS):
    _element = None
    __element = None

    locator: str = None
    locator_type: str = None
    name: str = None
    parent: Any = None
    wait: bool = None

    @property
    def element(self) -> Union[SeleniumWebElement, AppiumWebElement, PlayWebElement]:
        """
        Get WebElement object depending on current driver

        :return: Union[SeleniumWebElement, AppiumWebElement, PlayWebElement]
        """
        raise NotImplementedError()

    @element.setter
    def element(self, base_element: Union[SeleniumWebElement, AppiumWebElement, PlayWebElement]):
        """
        Element object setter. Try to avoid usage of this function

        :param: Union[SeleniumWebElement, AppiumWebElement, PlayWebElement]
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def all_elements(self) -> Union[list, List[Any]]:
        """
        Get all wrapped elements with playwright bases

        :return: list of wrapped objects
        """
        raise NotImplementedError()

    def click(self, with_wait: bool = True, *args, **kwargs) -> ElementABS:
        """
        Click to current element

        :param with_wait: wait for element before click

        Selenium/Appium:
        :param: args: compatibility arg
        :param: kwargs: compatibility arg

        Playwright:
        :param: args: additional params https://playwright.dev/python/docs/api/class-locator#locator-click
        :param: kwargs: additional params https://playwright.dev/python/docs/api/class-locator#locator-click

        :return: self
        """
        raise NotImplementedError()

    def click_into_center(self, silent: bool = False) -> ElementABS:
        """
        Click into the center of element

        :param silent: erase log message
        :return: self
        """
        raise NotImplementedError()

    def type_text(self, text: Union[str, KeyboardKeys], silent: bool = False) -> ElementABS:
        """
        Type text to current element

        :param: text: text to be typed
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    def type_slowly(self, text: str, sleep_gap: float = 0.05, silent: bool = False) -> ElementABS:
        """
        Type text to current element slowly

        :param: text: text to be slowly typed
        :param: sleep_gap: sleep gap before each key press
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    def clear_text(self, silent: bool = False) -> ElementABS:
        """
        Clear text from current element

        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    def check(self) -> ElementABS:
        """
        Check current checkbox

        :return: self
        """
        raise NotImplementedError()

    def uncheck(self) -> ElementABS:
        """
        Uncheck current checkbox

        :return: self
        """
        raise NotImplementedError()

    def wait_element(self, timeout: int = WAIT_EL, silent: bool = False) -> ElementABS:
        """
        Wait for current element available in page

        :param: timeout: time to stop waiting
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    def wait_element_hidden(self, timeout: int = WAIT_EL, silent: bool = False) -> ElementABS:
        """
        Wait until current element hidden

        :param: timeout: time to stop waiting
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    def wait_availability(self, timeout: int = WAIT_EL, silent: bool = False) -> ElementABS:
        """
        Wait for current element available in DOM

        :param: timeout: time to stop waiting
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    def get_screenshot(self, filename: str) -> Image:
        """
        Taking element screenshot and saving with given path/filename

        :param filename: path/filename
        :return: image binary
        """
        raise NotImplementedError()

    def screenshot_base(self) -> Image:
        raise NotImplementedError()

    @property
    def text(self) -> str:
        """
        Get text from current element

        :return: element text
        """
        raise NotImplementedError()

    def inner_text(self) -> str:
        """
        Get current element inner text

        :return: element inner text
        """
        raise NotImplementedError()

    def value(self) -> str:
        """
        Get value from current element

        :return: element value
        """
        raise NotImplementedError()

    def is_available(self) -> bool:
        """
        Check current element availability in DOM

        :return: True if present in DOM
        """
        raise NotImplementedError()

    def is_displayed(self, silent: bool = False) -> bool:
        """
        Check visibility of element

        :param: silent: erase log
        :return: True if element visible
        """
        raise NotImplementedError()

    def is_hidden(self, silent: bool = False) -> bool:
        """
        Check invisibility of current element

        :param: silent: erase log
        :return: True if element hidden
        """
        raise NotImplementedError()

    def get_attribute(self, attribute: str, silent: bool = False) -> str:
        """
        Get custom attribute from current element

        :param: attribute: custom attribute: value, innerText, textContent etc.
        :param: silent: erase log
        :return: custom attribute value
        """
        raise NotImplementedError()

    def get_elements_texts(self, silent: bool = False) -> List[str]:
        """
        Get all texts from all matching elements

        :param: silent: erase log
        :return: list of texts
        """
        raise NotImplementedError()

    def get_elements_count(self, silent: bool = False) -> int:
        """
        Get elements count

        :param: silent: erase log
        :return: elements count
        """
        raise NotImplementedError()

    def get_rect(self) -> dict:
        """
        A dictionary with the size and location of the element.

        :return: dict ~ {'y': 0, 'x': 0, 'width': 0, 'height': 0}
        """
        raise NotImplementedError()

    def is_enabled(self, silent: bool = False) -> bool:
        """
        Check if element enabled

        :param silent: erase log
        :return: True if element enabled
        """
        raise NotImplementedError()

    def is_checked(self) -> bool:
        """
        Is checkbox checked

        :return: bool
        """
        raise NotImplementedError()

    def hover(self, silent: bool = False) -> ElementABS:
        """
        Hover over current element

        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    def hover_outside(self, x: int = 0, y: int = -5) -> ElementABS:
        """
        Hover outside from current element. By default, 5px above  of element

        :param x: x-offset of element to hover
        :param y: y-offset of element to hover
        :return: self
        """
        raise NotImplementedError()

    def click_outside(self, x: int = -1, y: int = -1) -> ElementABS:
        """
        Click outside of element. By default, 1px above and 1px left of element

        :param x: x offset of element to click
        :param y: y offset of element to click
        :return: self
        """
        raise NotImplementedError()

    def click_in_alert(self) -> ElementABS:
        """
        Mobile only:
        Click on element in alert with switch to native context

        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def set_text(self, text: str, silent: bool = False) -> ElementABS:
        """
        Set (clear and type) text in current element

        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def send_keyboard_action(self, action: Union[str, KeyboardKeys]) -> ElementABS:
        """
        Send keyboard action to current element

        :param action: keyboard action
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_elements_count(
            self,
            expected_count: int,
            timeout: Union[int, float] = WAIT_EL,
            silent: bool = False
    ) -> ElementABS:
        """
        Wait until elements count will be equal to expected value

        :param: elements_count: expected elements count
        :param: timeout: wait timeout
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_element_text(
            self,
            timeout: Union[int, float] = WAIT_EL,
            silent: bool = False
    ) -> ElementABS:
        """
        Wait non empty text in element

        :param timeout: wait timeout
        :param silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_element_value(
            self,
            timeout: Union[int, float] = WAIT_EL,
            silent: bool = False
    ) -> ElementABS:
        """
        Wait non empty value in element

        :param timeout: wait timeout
        :param silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_element_without_error(
            self,
            timeout: [int, float] = WAIT_EL,
            silent: bool = False
    ) -> ElementABS:
        """
        Wait until element visibility without error

        :param: timeout: time to stop waiting
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_element_hidden_without_error(
            self,
            timeout: [int, float] = WAIT_EL,
            silent: bool = False
    ) -> ElementABS:
        """
        Wait until element hidden without error

        :param: timeout: time to stop waiting
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_enabled(self, timeout: [int, float] = WAIT_EL, silent: bool = False) -> ElementABS:
        """
        Wait until element clickable

        :param: timeout: time to stop waiting
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_disabled(self, timeout: [int, float] = WAIT_EL, silent: bool = False) -> ElementABS:
        """
        Wait until element clickable

        :param: timeout: time to stop waiting
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def is_visible(self, silent: bool = False, check_displaying: bool = True) -> bool:
        """
        Check is current element top left corner or bottom right corner visible on current screen

        :param silent: erase log
        :param check_displaying: trigger is_displayed additionally
        :return: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def is_fully_visible(self, silent: bool = False, check_displaying: bool = True) -> bool:
        """
        Check is current element top left corner and bottom right corner visible on current screen

        :param silent: erase log
        :param check_displaying: trigger is_displayed additionally
        :return: bool
        """
        raise NotImplementedError()

    def scroll_into_view(
            self,
            block: str = 'center',
            behavior: str = 'instant',
            sleep: Union[int, float] = 0,
            silent: bool = False,
    ) -> ElementABS:
        """
        Scroll element into view by js script

        :param: block: start - element on the top; end - element at the bottom. All: start, center, end, nearest
        :param: behavior: scroll type: smooth or instant
        :param: sleep: delay after scroll
        :param: silent: erase log
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def assert_screenshot(
            self,
            filename: str = '',
            test_name: str = '',
            name_suffix: str = '',
            threshold: Union[int, float] = None,
            delay: Union[int, float] = None,
            scroll: bool = False,
            remove: Union[Any, List[Any]] = None,
            fill_background: Union[str, bool] = False
    ) -> None:
        """
        Assert given (by name) and taken screenshot equals

        :param filename: full screenshot name. Custom filename will be used if empty string given
        :param test_name: test name for custom filename. Will try to find it automatically if empty string given
        :param name_suffix: filename suffix. Good to use for same element with positive/netagative case
        :param threshold: possible threshold
        :param delay: delay before taking screenshot
        :param scroll: scroll to element before taking the screenshot
        :param remove: remove elements from screenshot
        :param fill_background: fill background with given color or black color by default
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def get_element_info(self, element: Any = None) -> str:
        """
        Get full loging data depends on parent element

        :param element: element to collect log data
        :return: log string
        """
        raise NotImplementedError()

    def _get_all_elements(self, sources: Union[tuple, list]) -> List[Any]:
        """
        Get all wrapped elements from sources

        :param sources: list of elements: `all_elements` from selenium or `element_handles` from playwright
        :return: list of wrapped elements
        """
        raise NotImplementedError()