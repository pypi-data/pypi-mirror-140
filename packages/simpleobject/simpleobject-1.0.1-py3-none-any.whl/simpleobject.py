class simpleobject(dict):
    '''Simple json serializable object'''

    def __str__(self):
        name_key = '__name__' if '__name__' in self else 'name' if 'name' in self else None
        name = self[name_key] if name_key in self else 'simpleobject'
        values = ', '.join(f'{k}={v!r}' for k,v in self.items() if k != name_key)
        return f'{name}({values})'

    def __repr__(self):
        return self.__str__()

    def __setattr__(self, k, v):
        self[k] = v

    def __getattr__(self, k):
        return self[k]

    def __delattr__(self, k):
        del self[k]
