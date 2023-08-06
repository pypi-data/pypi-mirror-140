from typing import Any, Callable, Dict, List
from functools import reduce

from attrs import field


class Value:
    def __init__(
        self,
        name: str = None,
        *,
        from_list: bool = None,
        **field_kwargs: Dict[str, Any],
    ):
        """A wrapper over attrs' field function

        :param name: Value name. If specified, this will be used as the key instead of the attribute name
        :type name: str
        :param from_list: Whether the converter and validators should be applied on each list item
        :type from_list: bool
        :param field_kwargs: Attrs field keyword arguments
        :type field_kwargs: Dict[str, Any]

        """
        self.name = name
        self.field_property_kwargs: Dict[str, Any] = {}

        self.from_list_input = from_list

        self.field_kwargs = field_kwargs
        self.path = []

    def _update_field_keywords(self):
        """Called before the :func:`~attrs_mek.Value.to_field` method"""

        # If from_list = True then we want to change the converter function
        # to apply over a list
        if self.from_list_input is not None and "converter" in self.field_kwargs:
            converter = self.field_kwargs["converter"]

            def list_converter_func(values):
                return [converter(val) for val in values]

            self.field_kwargs["converter"] = list_converter_func

        # If from_list = True then we want to change the validator function
        # to apply over a list
        if self.from_list_input is not None and "validator" in self.field_kwargs:
            validator = self.field_kwargs["validator"]

            def list_validator_func(values):
                return [validator(val) for val in values]

            self.field_kwargs["validator"] = list_validator_func

    def validator(self, validator: Callable[[Any, Any, Any], Any]):
        """
        Attrs field validator

        :param validator: Value validator function to be handled by attrs
        :type validator: (cls, attribute, value) -> Any

        >>> @mek
        ... class Person:
        ...     name: str = Value()
        ...
        ...     @date.validator
        ...     def date_validator(cls, attribute, name):
        ...         return isinstance(name, str)
        """
        self.field_property_kwargs["validator"] = validator

    def default(self, default: Any):
        """Attrs default value"""
        self.field_property_kwargs["default"] = default

    def converter(self, converter: Callable[[Any], Any]):
        """
        Attrs field converter

        :param converter: Value converter function to be handled by attrs
        :type converter: Any -> Any

        >>> @mek
        ... class Person:
        ...     date: datetime = Value()
        ...
        ...     @date.converter
        ...     def date_converter(val: str):
        ...         return datetime.strptime(val, "%Y/%m/%d")
        """
        self.field_property_kwargs["converter"] = converter

    def from_list(
        self, from_list: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    ):
        """Combine list elements with top level data

        :param from_list: Function that takes in the entire response dictionary and each listm item and returns the desired merge.
        :type from_list: (Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]

        >>> response = {
        ...     "people": [
        ...         {"name": "Mek", "age": 0},
        ...         {"name": "Mek2", "age": 10},
        ...     ],
        ...     "status": {"date": "2022/1/1"},
        ... }
        ...
        >>> @mek
        ... class Person:
        ...     name: str
        ...     age: int
        ...     date: datetime = Value(converter=lambda x: datetime.strptime(x, "%Y/%m/%d"))
        ...
        >>> @mek
        ... class People:
        ...     people: List[Person] = Value(converter=Person.from_dict)
        ...
        ...     @people.from_list
        ...     def combiner(dictionary, people_item):
        ...         return {**dictionary["status"], **people_item}

        """
        self.from_list_input = from_list

    def from_list_merge(
        self,
        from_list: Callable[[Dict[str, Any]], Dict[str, Any]] = None,
        *,
        override_item: bool = False,
    ):
        """Simple dictionary merge each list item.

        This function is a short hand for the :func:`~attrs_mek.Value.from_list` when you just need to merge the two dictionaries.

        :param from_list: Fucntion whose return is merged with each list item
        :type from_list: Dict[str, Any] -> Dict[str, Any]
        :param override_item: Whether this return value should override any key collisions in the list item (True) or whether the list item should override key collisions with the return of this function (False)
        :type override_item: bool

        >>> response = {
        ...     "people": [
        ...         {"name": "Mek", "age": 0},
        ...         {"name": "Mek2", "age": 10},
        ...     ],
        ...     "status": {"date": "2022/1/1"},
        ... }
        ...
        >>> @mek
        ... class Person:
        ...     name: str
        ...     age: int
        ...     date: datetime = Value(converter=lambda x: datetime.strptime(x, "%Y/%m/%d"))
        ...
        >>> @mek
        ... class People:
        ...     people: List[Person] = Value(converter=Person.from_dict)
        ...
        ...     @people.from_list_merge(override_item=False)
        ...     def combiner(dictionary):
        ...         return dictionary["status"]

        This example achieves the same results as in :func:`~attrs_mek.Value.from_list`
        """

        def from_list_decoratator(from_list):
            if override_item:
                func = lambda x, li: {**li, **from_list(x)}
            else:
                func = lambda x, li: {**from_list(x), **li}

            self.from_list_input = func

        if from_list is None:
            return from_list_decoratator

        from_list_decoratator(from_list)

    def _set_path(self, path: List[str]):
        self.path = path

    def _get_value(self, path_to_field: List[str], dictionary: Dict[str, Any]) -> Any:
        """In the from_dict method, get this value from the input dictionary

        :param path_to_field: Path to this value, with variables filled in
        :type path_to_field: List[str]
        :param dictionary: from_dict input
        :type dictionary: Dict[str, Any]
        """

        def reduce_func(nested_dictionary, nested_key):
            return nested_dictionary[nested_key]

        # Traverse the list of nested key names to get the value
        value = reduce(reduce_func, path_to_field, dictionary)

        if self.from_list_input is not None and not isinstance(self.from_list, bool):
            # If there is a from_list function and it is not a boolean, i.e.
            # it was already applied to the attrs converter
            return [self.from_list_input(dictionary, val) for val in value]

        return value

    def _to_field(self):
        """Get the field from this value, to set before attrs define"""

        # Any field transformations:
        self._update_field_keywords()

        return field(**self.field_property_kwargs, **self.field_kwargs)
