"""
This file contains code for the library "ObjectAsString".
Author: DigitalCreativeApkDev
"""

# Importing necessary libraries


import copy
from mpmath import mp, mpf
mp.pretty = True


# Creating method to check whether an object is a number or not


def is_number(obj: object) -> bool:
    try:
        mpf(obj)
        return True
    except Exception:
        return False


class ObjectAsString:
    """
    This class contains attributes of string representation of an object.
    """

    def __init__(self, obj):
        # type: (object) -> None
        self.obj: object = obj

    def __len__(self):
        # type: () -> int
        if isinstance(self.obj, str) or isinstance(self.obj, list):
            return len(self.obj)
        raise Exception("Unsupported operation '__len__' for type '" + str(type(self.obj)) + "'!")

    def __add__(self, other):
        # type: (object) -> ObjectAsString
        if isinstance(other, ObjectAsString):
            try:
                if is_number(self.obj) and is_number(other.obj):
                    return ObjectAsString(mpf(self.obj + other.obj))
                elif isinstance(self.obj, list) and isinstance(other.obj, list):
                    return ObjectAsString(self.obj + other.obj)
                else:
                    return ObjectAsString(str(self.obj + other.obj))
            except TypeError:
                return ObjectAsString(str(self.obj) + str(other.obj))
        else:
            try:
                if is_number(self.obj) and is_number(other):
                    return ObjectAsString(mpf(self.obj + other))
                elif isinstance(self.obj, list) and isinstance(other, list):
                    return ObjectAsString(self.obj + other)
                else:
                    return ObjectAsString(str(self.obj + other))
            except TypeError:
                return ObjectAsString(str(self.obj) + str(other))

    def __sub__(self, other):
        # type: (object) -> ObjectAsString
        if isinstance(other, ObjectAsString):
            if dir(type(self.obj)).__contains__('__sub__') and \
                    dir(type(other.obj)).__contains__('__sub__'):
                if is_number(self.obj) and is_number(other.obj):
                    return ObjectAsString(mpf(self.obj - other.obj))
                return ObjectAsString(str(self.obj - other.obj))
            else:
                raise Exception("Unsupported operand type '-' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other.obj)) + "'!")
        else:
            if dir(type(self.obj)).__contains__('__sub__') and \
                    dir(type(other)).__contains__('__sub__'):
                if is_number(self.obj) and is_number(other):
                    return ObjectAsString(mpf(self.obj - other))
                return ObjectAsString(str(self.obj - other))
            else:
                raise Exception("Unsupported operand type '-' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other)) + "'!")

    def __mul__(self, other):
        # type: (object) -> ObjectAsString
        if isinstance(other, ObjectAsString):
            if dir(type(self.obj)).__contains__('__mul__') and \
                    dir(type(other.obj)).__contains__('__mul__'):
                if is_number(self.obj) and is_number(other.obj):
                    return ObjectAsString(mpf(self.obj * other.obj))
                elif isinstance(self.obj, list) and isinstance(other.obj, int):
                    return ObjectAsString(self.obj * other.obj)
                elif isinstance(other.obj, list) and isinstance(self.obj, int):
                    return ObjectAsString(other.obj * self.obj)
                else:
                    return ObjectAsString(str(self.obj * other.obj))
            else:
                raise Exception("Unsupported operand type '*' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other.obj)) + "'!")
        else:
            if dir(type(self.obj)).__contains__('__mul__') and \
                    dir(type(other)).__contains__('__mul__'):
                if is_number(self.obj) and is_number(other):
                    return ObjectAsString(mpf(self.obj * other))
                elif isinstance(self.obj, list) and isinstance(other, int):
                    return ObjectAsString(self.obj * other)
                elif isinstance(other, list) and isinstance(self.obj, int):
                    return ObjectAsString(other * self.obj)
                else:
                    return ObjectAsString(str(self.obj * other))
            else:
                raise Exception("Unsupported operand type '*' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other)) + "'!")

    def __truediv__(self, other):
        # type: (object) -> ObjectAsString
        if isinstance(other, ObjectAsString):
            if dir(type(self.obj)).__contains__('__truediv__') and \
                    dir(type(other.obj)).__contains__('__truediv__'):
                if is_number(self.obj) and is_number(other.obj):
                    return ObjectAsString(mpf(self.obj / other.obj))
                return ObjectAsString(str(self.obj / other.obj))
            else:
                raise Exception("Unsupported operand type '/' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other.obj)) + "'!")
        else:
            if dir(type(self.obj)).__contains__('__truediv__') and \
                    dir(type(other)).__contains__('__truediv__'):
                if is_number(self.obj) and is_number(other):
                    return ObjectAsString(mpf(self.obj / other))
                return ObjectAsString(str(self.obj / other))
            else:
                raise Exception("Unsupported operand type '/' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other)) + "'!")

    def __floordiv__(self, other):
        # type: (object) -> ObjectAsString
        if isinstance(other, ObjectAsString):
            if dir(type(self.obj)).__contains__('__floordiv__') and \
                    dir(type(other.obj)).__contains__('__floordiv__'):
                if is_number(self.obj) and is_number(other.obj):
                    return ObjectAsString(mpf(self.obj // other.obj))
                return ObjectAsString(str(self.obj // other.obj))
            else:
                raise Exception("Unsupported operand type '//' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other.obj)) + "'!")
        else:
            if dir(type(self.obj)).__contains__('__floordiv__') and \
                    dir(type(other)).__contains__('__floordiv__'):
                if is_number(self.obj) and is_number(other):
                    return ObjectAsString(mpf(self.obj // other))
                return ObjectAsString(str(self.obj // other))
            else:
                raise Exception("Unsupported operand type '//' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other)) + "'!")

    def __mod__(self, other):
        # type: (object) -> ObjectAsString
        if isinstance(other, ObjectAsString):
            if dir(type(self.obj)).__contains__('__mod__') and \
                    dir(type(other.obj)).__contains__('__mod__'):
                if is_number(self.obj) and is_number(other.obj):
                    return ObjectAsString(mpf(self.obj % other.obj))
                return ObjectAsString(str(self.obj % other.obj))
            else:
                raise Exception("Unsupported operand type '%' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other.obj)) + "'!")
        else:
            if dir(type(self.obj)).__contains__('__mod__') and \
                    dir(type(other)).__contains__('__mod__'):
                if is_number(self.obj) and is_number(other):
                    return ObjectAsString(mpf(self.obj % other))
                return ObjectAsString(str(self.obj % other))
            else:
                raise Exception("Unsupported operand type '%' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other)) + "'!")

    def __pow__(self, other):
        # type: (object) -> ObjectAsString
        if isinstance(other, ObjectAsString):
            if dir(type(self.obj)).__contains__('__pow__') and \
                    dir(type(other.obj)).__contains__('__pow__'):
                if is_number(self.obj) and is_number(other.obj):
                    return ObjectAsString(mpf(self.obj ** other.obj))
                return ObjectAsString(str(self.obj ** other.obj))
            else:
                raise Exception("Unsupported operand type '**' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other.obj)) + "'!")
        else:
            if dir(type(self.obj)).__contains__('__pow__') and \
                    dir(type(other)).__contains__('__pow__'):
                if is_number(self.obj) and is_number(other):
                    return ObjectAsString(mpf(self.obj ** other))
                return ObjectAsString(str(self.obj ** other))
            else:
                raise Exception("Unsupported operand type '**' for type '" + str(type(self.obj))
                                + "' with type '" + str(type(other)) + "'!")

    def __gt__(self, other):
        # type: (object) -> bool
        if isinstance(other, ObjectAsString):
            return self.obj > other.obj
        return self.obj > other

    def __ge__(self, other):
        # type: (object) -> bool
        if isinstance(other, ObjectAsString):
            return self.obj >= other.obj
        return self.obj >= other

    def __lt__(self, other):
        # type: (object) -> bool
        if isinstance(other, ObjectAsString):
            return self.obj < other.obj
        return self.obj < other

    def __le__(self, other):
        # type: (object) -> bool
        if isinstance(other, ObjectAsString):
            return self.obj <= other.obj
        return self.obj <= other

    def __eq__(self, other):
        # type: (object) -> bool
        if isinstance(other, ObjectAsString):
            return self.obj == other.obj
        return self.obj == other

    def __ne__(self, other):
        # type: (object) -> bool
        if isinstance(other, ObjectAsString):
            return self.obj != other.obj
        return self.obj != other

    def __str__(self):
        # type: () -> str
        return str(self.obj)

    def clone(self):
        # type: () -> ObjectAsString
        return copy.deepcopy(self)
