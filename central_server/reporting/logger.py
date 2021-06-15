from abc import ABC
from termcolor import colored


class Logger(ABC):
    @property
    def name(self) -> str:
        raise NotImplementedError(self.__name__ + '.name')

    def print(self, *args, **kwargs):
        raise NotImplementedError(self.__name__ + '.print()')

    def warn(self, *args):
        raise NotImplementedError(self.__name__ + '.warn()')

    def info(self, *args):
        raise NotImplementedError(self.__name__ + '.info()')

    def error(self, *args):
        raise NotImplementedError(self.__name__ + '.error()')

    def debug(self, *args):
        raise NotImplementedError(self.__name__ + '.debug()')


class ProperLogger(Logger):
    def __init__(self, name: str = 'DEFAULT', never_color: bool = False, silent_levels: set = None):
        self._name = name
        self.never_color = never_color
        self.silent_levels = silent_levels if silent_levels is not None else {'debug'}

    @property
    def name(self) -> str:
        return self._name

    def print(self, *args, **kwargs):
        if 'color' not in kwargs:
            color = None
        elif self.never_color:
            color = None
        else:
            color = kwargs['color']
        text = f'[{self.name}]'
        if color is not None:
            text = colored(text, color=color)
        print(text, end=' ')
        print(*args)

    def warn(self, *args):
        if 'warn' in self.silent_levels:
            return
        self.print(*args, color='yellow')

    def error(self, *args):
        if 'error' in self.silent_levels:
            return
        self.print(*args, color='red')

    def info(self, *args):
        if 'info' in self.silent_levels:
            return
        self.print(*args, color='green')

    def debug(self, *args):
        if 'debug' in self.silent_levels:
            return
        self.print(*args, color='blue')


class ShutUpLogger(Logger):
    def __init__(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return ''

    def print(self, *args, **kwargs):
        return

    def warn(self, *args):
        pass

    def info(self, *args):
        pass

    def error(self, *args):
        pass

    def debug(self, *args):
        pass


slave_api = ProperLogger(name='SLAVE_API')
center_api = ProperLogger(name='CENTER_API')
core_sched = ProperLogger(name='CORE_SCHED',
                          # silent_levels=set()
                          )
misc_info = ShutUpLogger(name='MISC')
