from __future__ import annotations

import os
import re
import time
import importlib
import json
import base64
from typing import Union, List, Any
from string import punctuation

import cv2
import numpy
from skimage.metrics import structural_similarity

from dyatel.exceptions import DriverWrapperException, TimeoutException
from dyatel.js_scripts import add_element_over_js, delete_element_over_js
from dyatel.mixins.logging import autolog
from dyatel.mixins.core_mixin import get_frame, get_element_info


class VisualComparison:

    visual_regression_path = ''
    test_item = None
    skip_screenshot_comparison = False
    visual_reference_generation = False
    hard_visual_reference_generation = False
    default_delay = 0.75
    default_threshold = 0

    def __init__(self, driver_wrapper, element):
        self.driver_wrapper = driver_wrapper
        self.dyatel_element = element

    def assert_screenshot(
            self,
            filename: str,
            test_name: str,
            name_suffix: str,
            threshold: Union[int, float],
            delay: Union[int, float],
            scroll: bool,
            remove: List[Any],
            fill_background: Union[str, bool],
    ) -> VisualComparison:
        """
        Assert given (by name) and taken screenshot equals

        :param filename: full screenshot name. Custom filename will be used if empty string given
        :param test_name: test name for custom filename. Will try to find it automatically if empty string given
        :param name_suffix: filename suffix. Good to use for same element with positive/negative case
        :param threshold: possible threshold
        :param delay: delay before taking screenshot
        :param scroll: scroll to element before taking the screenshot
        :param remove: remove elements from screenshot
        :param fill_background: fill background with given color or black color by default
        :return: self
        """
        remove = remove if remove else []

        if self.skip_screenshot_comparison:
            return self

        if filename:
            if name_suffix:
                filename = f'{filename}_{name_suffix}'
        else:
            filename = self._get_screenshot_name(test_name, name_suffix)

        root_path = self.visual_regression_path

        if not root_path:
            raise Exception('Provide visual regression path to environment. '
                            f'Example: {self.__class__.__name__}.visual_regression_path = "src"')

        root_path = root_path if root_path.endswith('/') else f'{root_path}/'
        reference_directory = f'{root_path}reference/'
        output_directory = f'{root_path}output/'
        diff_directory = f'{root_path}difference/'

        reference_file = f'{reference_directory}{filename}.png'
        output_file = f'{output_directory}{filename}.png'
        diff_file = f'{diff_directory}/diff_{filename}.png'

        os.makedirs(os.path.dirname(reference_directory), exist_ok=True)
        os.makedirs(os.path.dirname(output_directory), exist_ok=True)
        os.makedirs(os.path.dirname(diff_directory), exist_ok=True)

        if scroll:
            self.dyatel_element.scroll_into_view()

        def save_screenshot(screenshot_name):
            self._fill_background(fill_background)
            self._appends_dummy_elements(remove)
            time.sleep(delay)
            self.dyatel_element.get_screenshot(screenshot_name)
            self._remove_dummy_elements()

        if self.hard_visual_reference_generation:
            save_screenshot(reference_file)
            return self

        image = cv2.imread(reference_file)
        if isinstance(image, type(None)):
            save_screenshot(reference_file)

            if self.visual_reference_generation:
                return self

            self._disable_reruns()

            raise FileNotFoundError(f'Reference file "{reference_file}" not found, but its just saved. '
                                    f'If it CI run, then you need to commit reference files.')

        if self.visual_reference_generation:
            return self

        save_screenshot(output_file)
        self._assert_same_images(output_file, reference_file, diff_file, threshold)
        return self

    def _appends_dummy_elements(self, remove_data: list) -> VisualComparison:
        """
        Placed an element above each from given list and paints it black

        :param remove_data: list of elements to be fake removed
        :return: VisualComparison
        """
        for obj in remove_data:

            try:
                el = obj.element
            except TimeoutException:
                msg = f'Cannot find {obj.name} while removing background from screenshot. {get_element_info(obj)}'
                raise TimeoutException(msg)

            self.driver_wrapper.execute_script(add_element_over_js, el)
        return self

    def _remove_dummy_elements(self) -> VisualComparison:
        """
        Remove all dummy elements from DOM

        :return: VisualComparison
        """
        self.driver_wrapper.execute_script(delete_element_over_js)
        return self

    def _fill_background(self, fill_background_data) -> VisualComparison:
        """
        Fill background of element

        :param fill_background_data: fill background with given color or black color by default
        :return: VisualComparison
        """
        element = self.dyatel_element.element

        if fill_background_data is True:
            self.driver_wrapper.execute_script('arguments[0].style.background = "#000";', element)
        if fill_background_data and type(fill_background_data) is str:
            self.driver_wrapper.execute_script(f'arguments[0].style.background = "{fill_background_data}";', element)

        return self

    def _assert_same_images(self, actual_file: str, reference_file: str, filename: str,
                            threshold: Union[int, float]) -> VisualComparison:
        """
        Assert that given images are equal to each other

        :param actual_file: actual image path
        :param reference_file: reference image path
        :param filename: difference image name
        :param threshold: possible difference in percents
        :return: VisualComparison
        """
        reference_image = cv2.imread(reference_file)
        output_image = cv2.imread(actual_file)
        diff, actual_threshold = self._get_difference(reference_image, output_image)

        same_size = reference_image.size == output_image.size
        is_different = actual_threshold > threshold

        if is_different or not same_size:
            cv2.imwrite(filename, diff)
            self._attach_allure_diff(actual_file, reference_file, filename)

        base_error = f"The new screenshot '{actual_file}' did not match the reference '{reference_file}'."

        if not same_size:
            raise AssertionError(f'{base_error} Image size (width, height) is different: '
                                 f'Expected:{reference_image.size}, Actual: {output_image.size}.')
        if is_different:
            raise AssertionError(f"{base_error} Threshold is: {actual_threshold}; Possible threshold is: {threshold}")

        return self

    def _get_screenshot_name(self, test_function_name: str = '', name_suffix: str = '') -> str:
        """
        Get screenshot name

        :param test_function_name: execution test name. Will try to find it automatically if empty string given
        :return: custom screenshot filename:
          :::
          - playwright: test_screenshot_rubiks_cube_playwright_chromium
          - selenium: test_screenshot_rubiks_cube_mac_os_x_selenium_chrome
          - appium ios: test_screenshot_rubiks_cube_iphone_13_v_15_4_appium_safari
          - appium android: test_screenshot_rubiks_cube_pixel5_v_12_appium_chrome
          :::
        """
        test_function_name = test_function_name if test_function_name else getattr(self.test_item, 'name', '')
        if not test_function_name:
            back_frame = get_frame().f_back
            test_function_name = ''
            try:
                for _ in range(50):
                    if 'test' not in test_function_name or 'test' not in back_frame.f_code.co_filename:
                        back_frame = back_frame.f_back
                        test_function_name = back_frame.f_code.co_name
                    else:
                        break
            except AttributeError:
                raise Exception("Can't find test name. Please pass the test_name as parameter to assert_screenshot")
        else:
            test_function_name = test_function_name.replace('[', '_')  # required here for better separation

        if self.driver_wrapper.mobile:
            caps = self.driver_wrapper.driver.caps

            device_name = caps.get('customDeviceName', '')

            if self.driver_wrapper.is_android and not device_name:
                device_name = caps.get('avd', f'{caps.get("deviceManufacturer")}_{caps.get("deviceModel", "none")}')
            elif self.driver_wrapper.is_ios and not device_name:
                device_name = caps['deviceName']

            browser_name = caps['browserName']
            platform_version = caps['platformVersion']
            screenshot_name = f'{device_name}_v_{platform_version}_appium_{browser_name}'
        elif self.driver_wrapper.selenium:
            caps = self.driver_wrapper.driver.caps
            platform_name, browser_name = caps["platformName"], caps['browserName']
            screenshot_name = f'{platform_name}_selenium_{browser_name}'
        elif self.driver_wrapper.playwright:
            caps = self.driver_wrapper.instance
            screenshot_name = f'playwright_{caps.browser_type.name}'
        else:
            raise DriverWrapperException('Cant find current platform')

        name_suffix = f'_{name_suffix}_' if name_suffix else '_'

        screenshot_name = f'{test_function_name}_{self.dyatel_element.name}{name_suffix}{screenshot_name}'

        for item in (']', '"', "'"):
            screenshot_name = screenshot_name.replace(item, '')

        for item in punctuation + ' ':
            screenshot_name = screenshot_name.replace(item, '_')

        screenshot_name = self._remove_unexpected_underscores(screenshot_name)

        return screenshot_name.lower()

    @staticmethod
    def _get_difference(img1: numpy.ndarray, img2: numpy.ndarray) -> tuple[numpy.ndarray, float]:
        """
        Calculate difference between two images

        :param img1: image 1, numpy.ndarray
        :param img2: image 2, numpy.ndarray
        :return: (diff image, diff float value )
        """

        # Convert images to grayscale
        before_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between the two images
        (score, diff) = structural_similarity(before_gray, after_gray, full=True)
        score = score * 100

        # The diff image contains the actual image differences between the two images
        # and is represented as a floating point data type in the range [0,1]
        # so we must convert the array to 8-bit unsigned integers in the range
        # [0,255] before we can use it with OpenCV
        diff = (diff * 255).astype("uint8")
        diff_box = cv2.merge([diff, diff, diff])

        # Threshold the difference image, followed by finding contours to
        # obtain the regions of the two input images that differ
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        mask = numpy.zeros(img1.shape, dtype='uint8')
        filled_after = img2.copy()

        for c in contours:
            area = cv2.contourArea(c)
            if area > 40:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(img1, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.rectangle(img2, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.rectangle(diff_box, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.drawContours(mask, [c], 0, (255, 255, 255), -1)
                cv2.drawContours(filled_after, [c], 0, (0, 255, 0), -1)

        diff_image, percent_diff = filled_after, 100 - score
        return diff_image, percent_diff

    @staticmethod
    def _attach_allure_diff(actual_path: str, expected_path: str, diff_path: str) -> None:
        """
        Attach screenshots to allure screen diff plugin
        https://github.com/allure-framework/allure2/blob/master/plugins/screen-diff-plugin/README.md

        :param actual_path: path of actual image
        :param expected_path: path of expected image
        :param diff_path: path of diff image
        :return: None
        """
        allure = None

        try:
            allure = importlib.import_module('allure')
        except ModuleNotFoundError:
            autolog('Skip screenshot attaching due to allure module not found')

        if allure:

            diff_dict = {}
            for name, path in (('actual', actual_path), ('expected', expected_path), ('diff', diff_path)):
                image = open(path, 'rb')
                diff_dict.update({name: f'data:image/png;base64,{base64.b64encode(image.read()).decode("ascii")}'})
                image.close()

            allure.attach(name='diff', body=json.dumps(diff_dict), attachment_type='application/vnd.allure.image.diff')

    def _disable_reruns(self) -> None:
        """
        Disable reruns for pytest

        :return: None
        """
        try:
            pytest_rerun = importlib.import_module('pytest_rerunfailures')
        except ModuleNotFoundError:
            return None

        if hasattr(self.test_item, 'execution_count'):
            self.test_item.execution_count = pytest_rerun.get_reruns_count(self.test_item) + 1

    def _remove_unexpected_underscores(self, text) -> str:
        """
        Remove multiple underscores from given text

        :return: test_screenshot__data___name -> test_screenshot_data_name
        """
        return re.sub(r'_{2,}', '_', text)
