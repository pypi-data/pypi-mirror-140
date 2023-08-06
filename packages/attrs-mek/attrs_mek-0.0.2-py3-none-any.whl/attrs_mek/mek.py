from __future__ import annotations
from functools import reduce
from typing import Any, Dict, Tuple, List, Union

from attrs import define

from attrs_mek.key import BaseKey, Key, ChildKey, SiblingKey
from attrs_mek.value import Value

StrOrList = Dict[str, Union[str, List[str]]]


def _instance_of(type, expected):
    return str(type) == str(expected)


def _update_current_directory(key: BaseKey, current_path: List[str]):
    """Use key type to update the current directory"""
    key._update_path(current_path)


def _remove_key(cls, name: str):
    """Remove Key from object and annotations"""
    if name in cls.__annotations__:
        del cls.__annotations__[name]

    delattr(cls, name)


def _add_map_element(
    mapping: Dict[str, List[str]], name: str, value: Value, current_path: List[str]
):
    """Add Value path to mapping dictionary"""
    # use string in Value over attribute name:
    mapping_name = name if value.name is None else value.name

    value._set_path(current_path + [mapping_name])

    # add to mapping:
    mapping[mapping_name] = value


def _transform_value(cls, name: str, value_field: Value):
    """Convert mek.Value to attrs.field"""
    setattr(cls, name, value_field._to_field())


def _format_list(unformatted_list: List[str], variables: StrOrList):
    """Apply variables to value path from the mapping dictionary"""
    output = []

    for element in unformatted_list:
        if (
            element[0] + element[-1] == "{}"
            and (format_key := element[1:-1]) in variables
        ):
            # If list element is of the format: {name}, fill in variable
            format_value = variables[format_key]

            if isinstance(format_value, list) and len(format_value) > 0:
                # variable is a list
                output.extend(format_value)
            elif format_value != "" and format_value is not None:
                # variable is a single name
                output.append(format_value)
        else:
            output.append(element)

    return output


def _get_value_from_path(
    dictionary: Dict[str, Any],
    value: Value,
    variables: StrOrList,
) -> Tuple[Any, bool]:
    """Get single field value from path

    :returns: (value, to_keep)
    :rtype: (Any, bool)
    """
    try:
        path_to_field = _format_list(value.path, variables)
        return value._get_value(path_to_field, dictionary), True
    except (KeyError, TypeError):
        return None, False


def _from_dict(mapping: Dict[str, List[str]], global_variables: StrOrList):
    """Factory function for the attached from_dict"""

    @classmethod
    def from_dict(
        cls,
        input_dictionary: Dict[str, Any],
        variables: StrOrList = {},
    ):
        """Instantiate class from input dictionary

        :param input_dictionary: Data to load the class from
        :type input_dictionary: Dict[str, Any]
        :param variables: Dictionary of variable names and values to fill in path variables
        :type variables: Dict[str, str | List[str]]
        """
        output = {}
        variables = {**global_variables, **variables}

        for name, value in mapping.items():
            val, keep = _get_value_from_path(input_dictionary, value, variables)
            if keep:
                output[name] = val

        # Create attrs object:
        return cls(**output)

    return from_dict


def _mek_tranformations(
    cls,
    dict_items: List[Tuple[str, str]],
    mapping: StrOrList,
    current_directory: List[str],
):
    """Transform object to attrs compatible object"""
    for name, key_value_field in dict_items:
        if isinstance(key_value_field, Value):
            # Add value to the mapping dictionary
            _add_map_element(mapping, name, key_value_field, current_directory)

            # Update attribute to an attrs field in the object
            _transform_value(cls, name, key_value_field)
        elif isinstance(key_value_field, BaseKey):
            # Apply the key to the current list of nested keys
            _update_current_directory(key_value_field, current_directory)

            # Remove the key from the object
            _remove_key(cls, name)


def mek(cls=None, *, variables: StrOrList = {}, **attrs_kwargs: Dict[str, Any]):
    """
    ``attrs-mek`` class decorator

    :param variables: Key variable paths
    :type variables: str | List[str]
    :param attrs_kwargs: Attrs' decorator parameters passed into ``attrs.define``
    :type attrs_kwargs: Dict[str, Any]

    See examples `here <https://alrudolph.github.io/attrs-mek/examples.html>`_.
    """

    mapping = {}

    global_variables = variables.copy()

    def mek_with_class(cls):
        """mek decorator function"""
        current_directory = []

        annotations = list(cls.__annotations__.items())

        # Clean the object prior to transformations:
        if len(annotations) > 0:
            dict_items = {}
            attributes = cls.__dict__.copy()

            for name, type in annotations:
                if name in attributes:
                    dict_items[name] = attributes[name]
                    continue

                if _instance_of(type, Key):
                    set_value = Key(name, from_annotation=True)
                elif _instance_of(type, ChildKey):
                    set_value = ChildKey(name, from_annotation=True)
                elif _instance_of(type, SiblingKey):
                    set_value = SiblingKey(name, from_annotation=True)
                else:
                    set_value = Value(name)

                dict_items[name] = set_value
                setattr(cls, name, set_value)

            dict_items = dict_items.items()
        else:
            dict_items = cls.__dict__.copy().items()

        # TODO: Throw an error if there are non-type annotated fields
        # TODO: Make it so that keys don't need to be type annotated

        # Apply transformations:
        # * Store Values with their paths
        # * Remove keys from the object
        _mek_tranformations(cls, dict_items, mapping, current_directory)

        # Call the attrs define constructor, and add in the from_dict method
        attrs_cls = define(cls, **attrs_kwargs)
        attrs_cls.from_dict = _from_dict(mapping, global_variables)

        return attrs_cls

    return mek_with_class if cls is None else mek_with_class(cls)
