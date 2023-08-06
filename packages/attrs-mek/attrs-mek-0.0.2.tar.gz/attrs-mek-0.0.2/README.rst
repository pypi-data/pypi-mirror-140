``attrs-mek``: Nested deserialization for attrs
===============================================

``attrs-mek`` helps deserialize nested dictionaries into a flattened attrs object. This library provides functionality to:

1. Nested dictionary inputs
2. Nested dictionaries with variable key names and structures
3. Nested dictionaries with lists

See the full documentation `here <https://alrudolph.github.io/attrs-mek>`_.

Install from pip
----------------

.. code-block:: bash

    pip install attrs-mek

Basic Usage
-----------

.. code-block:: python

	from attrs_mek import mek
	
	person = {"name": "Mek", "age": 0}
	
	@mek
	class Person:
	    name: str
	    age: int
	
	mek_person = Person.from_dict(person)
	# Person(name="Mek", age=0)

The ``mek`` class decorator adds a ``from_dict`` class method to create an ``attrs`` object from a dictionary.
The result is entirely an ``attrs`` object with this added class method.

Handling Nested Dictionaries
----------------------------

The Key class allows you to specify the nested dictionary keys of the input dictionary.

.. code-block:: python

	from attrs_mek import mek, Key
	
	person = {"person": {"name": "Mek", "age": 0}}
	
	@mek
	class Person:
	    person: Key
	    name: str
	    age: int
	
	mek_person = Person.from_dict(person)
	# Person(name="Mek", age=0)

The ``person`` attribute with a Key type annotation specifies that all of the attributes below in the class
definition are nested within 'person' dictionary. This attribute is then removed from the attrs object.

Use the same ``attrs`` features
-------------------------------

``attrs-mek`` just handles initialization of an ``attrs`` object. Keyword arguments in the mek decorator
are passed into attrs' define and keyword arguments in the Value class are converted into attrs field's.

.. code-block:: python

	from datetime import datetime
	from attrs.validators import instance_of
	from attrs_mek import mek, Key, Value
	
	person = {
	    "person": {"name": "mek", "age": 0},
	    "meta": {"created": {"date": "2022/2/19"}},
	}
	
	def validate(cls, fields):
	    return [f.evolve(validator=instance_of(f.type)) for f in fields]
	
	@mek(frozen=True, field_transformer=validate)
	class Person:
	    person: Key
	    name: str = Value(converter=lambda name: name.title())
	    age: int
	
	    meta_created: Key
	    date: datetime = Value()
	
	    @date.converter
	    def date_converter(val: str):
	        return datetime.strptime(val, "%Y/%m/%d")
	
	mek_person = Person.from_dict(person)
	# Person(name='Mek', age=0, date=datetime.datetime(2022, 2, 19, 0, 0))

The object above is now frozen, which means an error will be thrown if you attempt to change a value, all fields
have a validator via attrs ``field_transformer`` and the name and date field have converters which are all handled by attrs.

The ``meta_key`` key in the example above also shows how you can use an underscore to specify multiple nested key levels.

Dealing with lists
------------------

``attrs-mek`` has a ``from_list`` parameter on Value objects which help dealing with list types.

.. code-block:: python

	response = {
	    "people": [
	        {"name": "Mek", "age": 0},
	        {"name": "Mek2", "age": 10},
	    ],
	    "status": {"date": "2022/1/1"},
	}
	
	@mek
	class Person:
	    name: str
	    age: int
	    date: datetime = Value(converter=lambda x: datetime.strptime(x, "%Y/%m/%d"))
	
	@mek
	class People:
	    people: List[Person] = Value(converter=Person.from_dict)
	    # Because a `from_list` is provided, the converter is applied to each list element.
	
	    @people.from_list
	    def combiner(dictionary, people_item):
	        # Combine the "status" dictionary with each element in "people"
	        # For simple cases like this, see :func:`~attrs_mek.Value.from_list_merge`
	        return {**dictionary["status"], **people_item}
	
	mek_person = People.from_dict(response)
	# People(people=[
	#   Person(name='Mek', age=0, date=datetime.datetime(2022, 1, 1, 0, 0)),
	#   Person(name='Mek2', age=10, date=datetime.datetime(2022, 1, 1, 0, 0))
	# ])                                  (line breaks added for readability)

In the example above, the ``combiner`` function combines the status nested dictionary with each element
in the people list. The specified converter function is then applied to each element in the list. 
