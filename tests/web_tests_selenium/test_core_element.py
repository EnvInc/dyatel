import random

import pytest


def test_element_storage(base_playground_page):
    page_element = base_playground_page.kube()
    assert page_element.element == page_element._elements


def test_elements_storage(base_playground_page):
    page_element = base_playground_page.any_link()
    storage_filled = page_element.all_elements == page_element._elements
    assert all((storage_filled, len(page_element._elements) > 1))


def test_element_displayed_positive(base_playground_page):
    assert base_playground_page.kube().is_displayed()


def test_element_displayed_negative(base_playground_page):
    assert not base_playground_page.kube_broken().is_displayed()


def test_parent_element_positive(base_playground_page):
    assert base_playground_page.kube_parent().is_displayed()


def test_parent_element_negative(base_playground_page):
    assert not base_playground_page.kube_broken_parent().is_displayed()


def test_click_and_wait(pizza_order_page):
    pizza_order_page.submit_button().click()
    after_click_displayed = pizza_order_page.error_modal().wait_element().is_displayed()
    pizza_order_page.error_modal().click_outside()
    after_click_outside_not_displayed = not pizza_order_page.error_modal().wait_element_hidden().is_displayed()
    assert all((after_click_displayed, after_click_outside_not_displayed))


def test_wait_without_error(pizza_order_page):
    pizza_order_page.error_modal().wait_element_without_error(timeout=0.01)
    assert not pizza_order_page.error_modal().is_displayed()


@pytest.mark.xfail_platform('android', reason='can not get text from that element')
def test_type_clear_text_get_value(pizza_order_page):
    text_to_send = str(random.randint(100, 9999))
    pizza_order_page.quantity_input().type_text(text_to_send)
    text_added = pizza_order_page.quantity_input().get_value == text_to_send
    pizza_order_page.quantity_input().clear_text()
    text_erased = pizza_order_page.quantity_input().get_value == ''
    assert all((text_added, text_erased))

