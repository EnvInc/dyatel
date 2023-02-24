from __future__ import annotations

from copy import copy
from typing import List, Any, Union

from dyatel.mixins.driver_mixin import DriverMixin
from dyatel.mixins.internal_utils import get_child_elements_with_names


def get_element_info(element: Any) -> str:
    """
    Get full loging data depends on parent element

    :param element: element to collect log data
    :return: log string
    """
    parent = element.parent
    current_data = f'Selector: ["{element.locator_type}": "{element.locator}"]'
    if parent:
        parent_data = f'Parent selector: ["{parent.locator_type}": "{parent.locator}"]'
        current_data = f'{current_data}. {parent_data}'
    return current_data


def set_parent_for_attr(instance_class: type, base_obj: object):
    """
    Copy attributes of given object and set new parent for him

    :param instance_class: attribute class to looking for
    :param base_obj: object of attribute
    :return: self
    """
    child_elements = get_child_elements_with_names(base_obj, instance_class).items()

    for name, child in child_elements:
        wrapped_child = copy(child)
        wrapped_child.parent = base_obj
        setattr(base_obj, name, wrapped_child)
        set_parent_for_attr(instance_class, wrapped_child)


class ElementMixin(DriverMixin):
    """ Mixin for PlayElement and CoreElement """

    def get_element_info(self, element: Any = None) -> str:
        """
        Get full loging data depends on parent element

        :param element: element to collect log data
        :return: log string
        """
        element = element if element else self
        return get_element_info(element)

    def _get_all_elements(self, sources: Union[tuple, list], instance_class: type) -> List[Any]:
        """
        Get all wrapped elements from sources

        :param sources: list of elements: `all_elements` from selenium or `element_handles` from playwright
        :param instance_class: attribute class to looking for
        :return: list of wrapped elements
        """
        wrapped_elements = []

        for element in sources:
            wrapped_object: Any = copy(self)
            wrapped_object.element = element
            wrapped_object._wrapped = True
            set_parent_for_attr(instance_class, wrapped_object)
            wrapped_elements.append(wrapped_object)

        return wrapped_elements
