# simpleobject
### Simple json serializable object

Can be used as a `types.SimpleNamespace`, but it is json serializable like a python dictionary.

### Install

`python -m pip install simpleobject`

### Usage
```python
from simpleobject import simpleobject
from json import dumps

o = simpleobject()
o.foo = 1
o.bar = 2
print(o) #simpleobject(foo=1, bar=2)
print(dumps(o)) #{"foo": 1, "bar": 2}
```

You can also set the name
```python
o.name = 'FooBarObject'
print(o) #FooBarObject(foo=1, bar=2)
```
