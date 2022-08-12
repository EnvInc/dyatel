import importlib
import math
import operator
import os
from functools import reduce
from logging import debug
from typing import Union

from PIL import Image, ImageChops


def assert_same_images(actual_file: str, reference_file: str, filename: str, threshold: Union[int, float]):
    reference_image = Image.open(reference_file).convert('RGB')
    output_image = Image.open(actual_file).convert('RGB')
    diff, actual_threshold = get_difference(reference_image, output_image)
    # TODO: Same size check
    # TODO: Same pixel ratio check
    if actual_threshold > threshold:
        root_path = os.environ.get('visual', '')
        diff_file = f'{root_path}/difference/diff-{filename}.png'
        diff.save(diff_file)
        attach_allure_diff(actual_file, reference_file, diff_file)
        raise AssertionError(f"The new screenshot '{actual_file}' did not match the"
                             f" reference '{reference_file}'. Threshold is: {actual_threshold}")


def get_difference(im1: Image, im2: Image):
    diff = ImageChops.difference(im1, im2)
    histogram = diff.histogram()

    red = reduce(
            operator.add,
            map(
                lambda h, i: h * (i ** 2),
                histogram,
                range(256)
            )
        )

    return diff, math.sqrt(red / (float(im1.size[0]) * im1.size[1]))


def attach_allure_diff(actual_path: str, expected_path: str, diff_path: str) -> None:
    """
    Attach screenshots to allure screen diff plugin
    https://github.com/allure-framework/allure2/blob/master/plugins/screen-diff-plugin/README.md

    Note: you should add pytest mark to your tests.

    Example::

        # Directly above the test
        @allure.label('testType', 'screenshotDiff')

        # Dynamically  in the fixtures/tests
        request.node.add_marker(allure.label('testType', 'screenshotDiff'))

    :param actual_path: path of actual image
    :param expected_path: path of expected image
    :param diff_path: path of diff image
    :return: None
    """
    try:
        allure = importlib.import_module('allure')
    except ModuleNotFoundError:
        allure = None
        debug('Skip screenshot attaching due to allure module not found')

    if allure:

        with open(actual_path, 'rb') as actual:
            image = actual.read()
            allure.attach(
                body=image,
                name='actual',
                attachment_type=allure.attachment_type.PNG
            )

        with open(expected_path, 'rb') as expected:
            image = expected.read()
            allure.attach(
                body=image,
                name='expected',
                attachment_type=allure.attachment_type.PNG
            )

        with open(diff_path, 'rb') as diff:
            image = diff.read()
            allure.attach(
                body=image,
                name='diff',
                attachment_type=allure.attachment_type.PNG
            )
