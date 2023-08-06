class Dictionary(dict):

    def __repr__(self):
        return '{' + ', '.join(f'{key}={value!r}' for key, value in self.items()) + '}'

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)
        
    @classmethod
    def from_dict(cls, target):
        if isinstance(target, dict):
            return cls({key: cls.from_dict(value) for key, value in target.items()})
        if isinstance(target, (list, tuple, set, frozenset)):
            return type(target)(cls.from_dict(item) for item in target)
        return target
    
    def to_dict(self, target=None):
        if target is None:
            target = self
        if isinstance(target, dict):
            return {key: self.to_dict(value) for key, value in target.items()}
        if isinstance(target, (list, tuple, set, frozenset)):
            return type(target)(self.to_dict(item) for item in target)
        return target