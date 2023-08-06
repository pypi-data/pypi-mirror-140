class CustomProperties():
    def __init__(self, jsonObj):
        self.__dict = jsonObj

        for name, value in jsonObj.items():
            setattr(self, name, value)
    
    def __getitem__(self, name):
        return self.__dict.get(name)

    def __iter__(self):
        return iter(self.__dict)

    def keys(self):
        return self.__dict.keys()

    def values(self):
        return self.__dict.values()

    def itervalues(self):
        return self.__dict.itervalues()

    def get(self, name, default=None):
        return self.__dict.get(name, default)