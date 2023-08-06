import inspect

from exceptions import OverrideException


def override(func):
    def wrapper(self):
        # We need this behavior to prevent calling not overridden function without creating an object.
        try:
            getattr(super(self.__class__, self), func.__name__)()
        except Exception:
            raise OverrideException('method was not overridden!')
        return func(self)

    return wrapper


class OverrideClass:
    def __init__(self):
        source_lines = inspect.getsourcelines(self.__class__)[0]
        for i, line in enumerate(source_lines):
            line = line.strip()
            if line.split('(')[0].strip() == '@' + 'override':
                next_line = source_lines[i + 1]
                name = next_line.split('def')[1].split('(')[0].strip()
                try:
                    getattr(super(self.__class__, self), name)()
                except Exception:
                    raise OverrideException('method was not overridden!')
