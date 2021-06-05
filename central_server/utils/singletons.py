

class Singletons(object):
    def __init__(self):
        self._instances = dict()

    def register(cls):
        self._instances[cls] = None

    def get(self, cls):
        if self._instances[cls] is None:
            # Initialization of singleton classes should not take any parameter
            self._instances[cls] = cls()
        return self._instance[cls]


singletons = Singletons()
