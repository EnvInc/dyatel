import pytest
from mock.mock import MagicMock

from dyatel.base.group import Group
from dyatel.dyatel_play.play_driver import PlayDriver
from dyatel.dyatel_play.play_element import PlayElement
from dyatel.dyatel_play.play_page import PlayPage
from dyatel.dyatel_sel.core.core_driver import CoreDriver
from dyatel.dyatel_sel.driver.mobile_driver import MobileDriver
from dyatel.dyatel_sel.driver.web_driver import WebDriver
from dyatel.dyatel_sel.elements.mobile_element import MobileElement
from dyatel.dyatel_sel.elements.web_element import WebElement
from dyatel.base.page import Page
from dyatel.base.element import Element
from dyatel.dyatel_sel.pages.mobile_page import MobilePage
from dyatel.dyatel_sel.pages.web_page import WebPage


@pytest.fixture
def mocked_mobile_driver():
    driver = MagicMock()
    driver.capabilities = MagicMock(return_value={'platformName': 'ios', 'browserName': 'safari'})()
    yield MobileDriver(driver)
    CoreDriver.driver = None


@pytest.fixture
def mocked_selenium_driver():
    yield WebDriver(MagicMock())
    CoreDriver.driver = None


@pytest.fixture
def mocked_play_driver():
    yield PlayDriver(MagicMock())
    PlayDriver.driver = None


def test_base_page_mobile(mocked_mobile_driver):
    page = Page('locator')
    assert all(
        (
            page.page_class == MobilePage,
            CoreDriver.mobile,
            page.__class__.__base__ == MobilePage
        )
    )


def test_base_element_mobile(mocked_mobile_driver):
    element = Element('locator')
    assert all(
        (
            element.element_class == MobileElement,
            CoreDriver.mobile,
            element.__class__.__base__ == MobileElement
        )
    )


def test_base_page_selenium(mocked_selenium_driver):
    page = Page('locator')
    assert all(
        (
            page.page_class == WebPage,
            not CoreDriver.mobile,
            page.__class__.__base__ == WebPage
        )
    )


def test_base_element_selenium(mocked_selenium_driver):
    element = Element('locator')
    assert all(
        (
            element.element_class == WebElement,
            not CoreDriver.mobile,
            element.__class__.__base__ == WebElement
        )
    )


def test_base_page_playwright(mocked_play_driver):
    page = Page('locator')
    assert all(
        (
            page.page_class == PlayPage,
            page.__class__.__base__ == PlayPage
        )
    )


def test_base_element_playwright(mocked_play_driver):
    element = Element('locator')
    assert all(
        (
            element.element_class == PlayElement,
            element.__class__.__base__ == PlayElement
        )
    )


def test_base_group_class_mobile(mocked_mobile_driver):
    group = Group('locator')
    assert all(
        (
            group.element_class == MobileElement,
            CoreDriver.mobile,
            group.__class__.__base__ == Element
        )
    )


def test_base_group_class_selenium(mocked_selenium_driver):
    group = Group('locator')
    assert all(
        (
            group.element_class == WebElement,
            not CoreDriver.mobile,
            group.__class__.__base__ == Element
        )
    )


def test_base_group_class_playwright(mocked_play_driver):
    group = Group('locator')
    assert all(
        (
            group.element_class == PlayElement,
            group.__class__.__base__ == Element
        )
    )
