"""
This file contains code for the library "PySortedSet".
Author: DigitalCreativeApkDev
"""


# Importing necessary library


import copy


# Creating static function to remove all from a list.


def unique(a_list: list) -> list:
    result: list = []  # initial value
    for elem in a_list:
        if elem not in result:
            result.append(elem)

    return result


class PySortedSet:
    """
    This class contains attributes of a sorted set in Python.
    """

    def __init__(self, elements=None):
        # type: (list) -> None
        if elements is None:
            elements = []
        elements.sort()
        self.elements: list = unique(elements)

    def clone(self):
        # type: () -> PySortedSet
        return copy.deepcopy(self)

    def __len__(self):
        # type: () -> int
        return len(self.elements)

    def __contains__(self, item):
        # type: (object) -> bool
        return item in self.elements

    def __and__(self, other):
        # type: (PySortedSet or list or set) -> PySortedSet
        # Implementing set intersection operation
        if isinstance(other, PySortedSet):
            curr_elements: list = self.clone().elements
            new_elements: list = []  # initial value
            for elem in curr_elements:
                if elem in other.elements:
                    new_elements.append(elem)

        elif isinstance(other, list):
            curr_elements: list = self.clone().elements
            new_elements: list = []  # initial value
            for elem in curr_elements:
                if elem in other:
                    new_elements.append(elem)

        else:
            curr_elements: list = self.clone().elements
            new_elements: list = []  # initial value
            for elem in curr_elements:
                if elem in list(other):
                    new_elements.append(elem)

        new_elements.sort()
        return PySortedSet(new_elements)

    def __add__(self, other):
        # type: (PySortedSet or list or set) -> PySortedSet
        # Implementing set union operation
        if isinstance(other, PySortedSet):
            new_elements: list = unique(self.clone().elements + other.clone().elements)
        elif isinstance(other, list):
            new_elements: list = unique(self.clone().elements + other)
        else:
            new_elements: list = unique(self.clone().elements + list(other))

        new_elements.sort()
        return PySortedSet(new_elements)

    def __sub__(self, other):
        # type: (PySortedSet or list or set) -> PySortedSet
        # Implementing set difference operation
        if isinstance(other, PySortedSet):
            new_elements: list = self.clone().elements
            for elem in unique(other.elements):
                if elem in new_elements:
                    new_elements.remove(elem)

        elif isinstance(other, list):
            new_elements: list = self.clone().elements
            for elem in unique(other):
                if elem in new_elements:
                    new_elements.remove(elem)

        else:
            new_elements: list = self.clone().elements
            for elem in unique(list(other)):
                if elem in new_elements:
                    new_elements.remove(elem)

        new_elements.sort()
        return PySortedSet(new_elements)

    def __getitem__(self, index):
        # type: (int) -> object
        if index < 0 or index >= len(self.elements):
            raise(Exception("PySortedSet index is out of range!"))
        return self.elements[index]

    def __setitem__(self, index, value):
        # type: (int, object) -> None
        self.elements[index] = value
        self.elements.sort()

    def add(self, value):
        # type: (object) -> PySortedSet
        new_elements: list = self.elements
        new_elements.append(value)
        new_elements.sort()
        return PySortedSet(new_elements)

    def remove(self, value):
        # type: (object) -> PySortedSet
        if value in self.elements:
            new_elements: list = self.elements
            new_elements.remove(value)
            new_elements.sort()
            return PySortedSet(new_elements)
        raise Exception("Cannot remove '" + str(value) + "' from PySortedSet because '"
                        + str(value) + "' is not in the set.")

    def __iter__(self):
        self.a = 0
        return self

    def __next__(self):
        if self.a < len(self.elements):
            x = self.elements[self.a]
            self.a += 1
            return x
        else:
            raise StopIteration

    def pop(self, index):
        # type: (int) -> object
        if index < 0 or index >= len(self.elements):
            raise (Exception("PySortedSet index is out of range!"))
        else:
            new_elements: list = self.elements
            to_be_returned: object = new_elements.pop(index)
            new_elements.sort()
            return to_be_returned

    def __str__(self):
        # type: () -> str
        res: str = "{"  # initial value
        for i in range(len(self.elements)):
            if i == len(self.elements) - 1:
                res += str(self.elements[i])
            else:
                res += str(self.elements[i]) + ", "

        return res + "}"

    def __eq__(self, other):
        # type: (object) -> bool
        if isinstance(other, PySortedSet):
            return self.elements == other.elements
        elif isinstance(other, list):
            return self.elements == unique(other)
        elif isinstance(other, set):
            return self.elements == unique(list(other))
        return False
