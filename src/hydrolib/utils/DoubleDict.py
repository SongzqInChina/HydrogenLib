class DoubleDict(dict):
    def __init__(self, dct):
        super().__init__()
        for k, v in dct.items():
            self[k] = v

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().__setitem__(value, key)

    def __delitem__(self, key):
        super().__delitem__(self[key])
        super().__delitem__(key)
