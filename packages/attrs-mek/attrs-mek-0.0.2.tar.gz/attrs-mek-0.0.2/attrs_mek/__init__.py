from attrs_mek.key import Key, SiblingKey, ChildKey
from attrs_mek.mek import mek
from attrs_mek.value import Value

__version__ = "0.0.2"

__title__ = "attrs-mek"
__description__ = "Nested deserialization for attrs"
__url__ = "https://alrudolph.github.io/attrs-mek"
__uri__ = __url__
__doc__ = f"`{__description__} <{__url__}>`_"

__author__ = "Alex Rudolph"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2022 Alex Rudolph"

__all__ = ["mek", "Value", "Key", "SiblingKey", "ChildKey"]
