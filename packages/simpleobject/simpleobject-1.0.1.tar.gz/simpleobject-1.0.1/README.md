# simpleobject
Simple json serializable object

### Usage
```python
from simpleobject import simpleobject
from json import dumps

o = simpleobject()
o.foo = 1
o.bar = 2
print(dumps(o)) #{"foo": 1, "bar": 2}
```