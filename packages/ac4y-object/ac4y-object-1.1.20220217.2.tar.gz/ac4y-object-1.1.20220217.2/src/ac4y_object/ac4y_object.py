class Ac4yObject(object):

    def __init__(self):
        self._dummy = None

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            self.__dict__[key] = value