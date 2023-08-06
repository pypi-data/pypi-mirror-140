import inspect

from exceptions import ConstException


class MetaConst(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise ConstException("Const can't be changed!")


class Const(object, metaclass=MetaConst):
    def __init__(self):

        # Use global variables because if we declare it as attribute it will cause exception.
        global attrs
        global attr_name

        # Get all subclass attributes
        attrs = set(dir(self.__class__)) - set(dir(Const))

        if len(attrs) > 1:
            raise ConstException("variables with Const type must have only 1 value!")

        attr_name = ''

        # Use inspect module to get attr values
        for i in inspect.getmembers(self.__class__):
            if not i[0].startswith('_'):

                if not inspect.ismethod(i[1]):
                    attr_name = i[1]
                else:
                    raise ConstException('Const type variable cannot have any methods!')

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise ConstException("Const can't be changed!")

    def __repr__(self):
        return str(attr_name)


class ConstNameSpace(object, metaclass=MetaConst):
    def __init__(self):
        # Use global variable because if we declare it as attribute it will cause exception.
        global attrs

        # Get all subclass attributes
        attrs = set(dir(self.__class__)) - set(dir(Const))

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise ConstException("Const can't be changed!")

    def __repr__(self):
        return str(attrs)
