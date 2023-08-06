"""
This file contains code for the library "StaticTypedList".
Author: DigitalCreativeApkDev
"""


# Importing necessary library


import copy


# Creating static function


def list_elements_type_match(elem_type: type, a_list: list) -> bool:
    for elem in a_list:
        if type(elem) != elem_type:
            return False
    return True


class StaticTypedList:
    """
    This class contains attributes of a static typed list in Python.
    """

    def __init__(self, elem_type=object, elements=None):
        # type: (type, list) -> None
        if elements is None:
            elements = []

        assert list_elements_type_match(elem_type, elements), "StaticTypedList element type mismatch!"
        self.elem_type: type = elem_type
        self.__elements: list = elements

    def __getitem__(self, index):
        # type: (int) -> object
        if index < -1 * len(self.__elements) or index >= len(self.__elements):
            raise Exception("StaticTypedList index is out of range!")
        return self.__elements[index]

    def __setitem__(self, index, value):
        # type: (int, object) -> None
        if index < -1 * len(self.__elements) or index >= len(self.__elements):
            raise Exception("StaticTypedList index is out of range!")
        self.__elements[index] = value

    def __len__(self):
        # type: () -> int
        return len(self.__elements)

    def __contains__(self, item):
        # type: (object) -> bool
        return item in self.__elements

    def __iter__(self):
        self.a = 0
        return self

    def __next__(self):
        if self.a < len(self.__elements):
            x = self.__elements[self.a]
            self.a += 1
            return x
        else:
            raise StopIteration

    def __eq__(self, other):
        # type: (object) -> bool
        if isinstance(other, StaticTypedList):
            return self.__elements == other.__elements
        elif isinstance(other, list):
            return self.__elements == other
        elif isinstance(other, set):
            return self.__elements == list(other)
        return False

    def append(self, elem):
        # type: (object) -> None
        if not issubclass(type(elem), self.elem_type):
            raise Exception("Cannot add '" + str(elem) + "' of type '" + str(type(elem)) +
                            " to StaticTypedList with type '" + str(self.elem_type) + "'!")
        self.__elements.append(elem)

    def extend(self, other):
        # type: (StaticTypedList) -> None
        if not issubclass(other.elem_type, self.elem_type):
            raise Exception("Cannot extend StaticTypedList of type '" + str(self.elem_type) +
                            "' with StaticTypedList of type '" + str(other.elem_type) + "'!")
        self.__elements.extend(other.__elements)

    def insert(self, index, elem):
        # type: (int, object) -> None
        if not issubclass(type(elem), self.elem_type):
            raise Exception("Cannot insert '" + str(elem) + "' of type '" + str(type(elem)) +
                            " to StaticTypedList with type '" + str(self.elem_type) + "'!")
        self.__elements.insert(index, elem)

    def remove(self, elem):
        # type: (object) -> bool
        if elem in self.__elements:
            self.__elements.remove(elem)
            return True
        return False

    def pop(self, index=-1):
        # type: (int) -> object
        if index < -1 * len(self.__elements) or index >= len(self.__elements):
            raise Exception("StaticTypedList index is out of range!")
        return self.__elements.pop(index)

    def count(self, elem):
        # type: (object) -> int
        return self.__elements.count(elem)

    def index(self, elem):
        # type: (object) -> int
        return self.__elements.index(elem)

    def reverse(self):
        # type: () -> None
        self.__elements.reverse()

    def sort(self):
        # type: () -> None
        self.__elements.sort()

    def clear(self):
        # type: () -> None
        self.__elements = []

    def __str__(self):
        # type: () -> str
        res: str = "["  # initial value
        for i in range(len(self.__elements)):
            if i == len(self.__elements) - 1:
                res += str(self.__elements[i])
            else:
                res += str(self.__elements[i]) + ", "

        return res + "]"

    def clone(self):
        # type: () -> StaticTypedList
        return copy.deepcopy(self)
