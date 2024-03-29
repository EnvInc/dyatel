def get_scroll_position(driver):
    return driver.execute_script('return window.pageYOffset || document.documentElement.scrollTop')


def test_swipe(second_playground_page, driver_wrapper):
    expected_scroll = range(300, 400) if driver_wrapper.is_android else range(1050, 1200)
    second_playground_page.swipe(0, 500, 0, 100, sleep=0.3)
    scroll = get_scroll_position(driver_wrapper.driver)
    assert scroll in expected_scroll
    second_playground_page.swipe(0, 100, 0, 500, sleep=0.3)
    scroll = get_scroll_position(driver_wrapper.driver)
    assert scroll == 0
