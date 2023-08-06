from abc import abstractclassmethod
from typing import List, Union

from attrs import define, field


@define
class BaseKey:
    path: List[str]
    type: str
    from_annotation: bool = field(default=False)

    def __attrs_post_init__(self):
        """Update the path"""

        # If the path name is passed into the constructor
        if not self.from_annotation:
            self.path = self._str_list_converter(self.path)
            return

        # If the path name is the attribute name:

        # Leading undescore resets path
        if self.path[0] == "_":
            self.path = []
            return

        # underscores in the middle of words represent nested keys
        split_path = [path for path in self.path.split("_") if path != ""]
        self.path = self._str_list_converter(split_path)

    @abstractclassmethod
    def _update_path(self, current_path: List[str]) -> None:
        """Use the key type to update the path"""
        raise NotImplementedError("_update_path must be called on a child Key object")

    @staticmethod
    def _str_list_converter(string: Union[str, List[str]]) -> List[str]:
        """path as list of strings"""
        if string is None or string == "":
            return []

        if isinstance(string, str):
            return [string]

        return string


class Key(BaseKey):
    """Specify nested dictionary keys, starting from the beginning

    :param path: Nested path of dictionary key names, surround value in {}'s to indicate a variable.
    :type path: str | List[str]

    As an annotation:

    >>> response = {"status": {"date": "2020-1-1"}, "other": {"nested": {"val": 10}}}
    >>> @mek
    ... class RequestItem():
    ...     status: Key
    ...     date: str
    ...     other_nested: Key
    ...     val: int

    Set to an attribute:

    >>> response = {"status": {"date": "2020-1-1"}, "other": {"nested": {"val": 10}}}
    >>> @mek
    ... class RequestItem():
    ...     _status = Key("status")
    ...     date: str
    ...     _other = Key(["other", "nested"])
    ...     val: int

    In the example above, the Key attribute names are only placeholders.
    """

    type: str = "root"

    def __init__(self, path: Union[str, List[str]] = None, **kwargs):
        super().__init__(path, self.type, **kwargs)

    def _update_path(self, current_path: List[str]):
        current_path[:] = self.path


class SiblingKey(BaseKey):
    """Specify nested dictionary keys, starting from the second to last key of the current position

    :param path: Nested path of dictionary key names, surround value in {}'s to indicate a variable.
    :type path: str | List[str]

    As an annotation:

    >>> response = {"other": {"nested": {"val": 10}, "status": {"date": "2020-1-1"}}}
    >>> @mek
    ... class RequestItem():
    ...     other_nested: Key
    ...     vaL: int
    ...     status: SiblingKey
    ...     date: str

    Set to an attribute:

    >>> response = {"other": {"nested": {"val": 10}, "status": {"date": "2020-1-1"}}}
    >>> @mek
    ... class RequestItem():
    ...     _nest_path = Key(["other", "nested"])
    ...     val: int
    ...     _status = SiblingKey(["status"])
    ...     date: str

    """

    type: str = "sibling"

    def __init__(self, path=None, **kwargs):
        super().__init__(path, self.type, **kwargs)

    def _update_path(self, current_path: List[str]):
        if len(current_path) > 0:
            current_path.pop()

        current_path.extend(self.path)


class ChildKey(BaseKey):
    """Specify nested dictionary keys, starting from the key of the current position

    :param path: Nested path of dictionary key names, surround value in {}'s to indicate a variable.
    :type path: str | List[str]

    As an annotation:

    >>> response = {"other": {"nested": {"val": 10, "status": {"date": "2020-1-1"}}}}
    >>> @mek
    ... class RequestItem():
    ...     other_nested: Key
    ...     val: int
    ...     status: ChildKey
    ...     date: str

    Set to an attribute:

    >>> response = {"other": {"nested": {"val": 10, "status": {"date": "2020-1-1"}}}}
    >>> @mek
    ... class RequestItem():
    ...     _other_nested: Key(["other", "nested"])
    ...     val: int
    ...     _status: ChildKey("status")
    ...     date: str

    """

    type: str = "child"

    def __init__(self, path=None, **kwargs):
        super().__init__(path, self.type, **kwargs)

    def _update_path(self, current_path: List[str]):
        current_path.extend(self.path)
