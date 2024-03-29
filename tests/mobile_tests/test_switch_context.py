def test_switch_context(driver_wrapper):
    assert driver_wrapper.get_current_context() == driver_wrapper.web_context_name
    assert driver_wrapper.is_web_context

    driver_wrapper.switch_to_native()
    assert driver_wrapper.get_current_context() == driver_wrapper.native_context_name
    assert driver_wrapper.is_native_context

    driver_wrapper.switch_to_web()
    assert driver_wrapper.get_current_context() == driver_wrapper.web_context_name
    assert driver_wrapper.is_web_context
