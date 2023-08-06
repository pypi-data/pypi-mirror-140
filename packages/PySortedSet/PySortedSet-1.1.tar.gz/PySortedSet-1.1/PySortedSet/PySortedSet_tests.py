import unittest
from PySortedSet import *


class MyTestCase(unittest.TestCase):
    def test_len(self):
        self.assertEquals(len(PySortedSet([1, 2, 5])), 3)
        self.assertEquals(len(PySortedSet([1, 2, 5, 3])), 4)
        self.assertEquals(len(PySortedSet([1, 2, 5, 5])), 3)
        a: PySortedSet = PySortedSet([5, 3])
        self.assertEquals(len(a), 2)
        self.assertEquals(len(a.add(7)), 3)
        self.assertEquals(len(a), 3)
        self.assertEquals(len(a.remove(5)), 2)
        self.assertEquals(len(a), 2)
        a.pop(1)
        self.assertEquals(len(a), 1)

    def test_intersection(self):
        a: PySortedSet = PySortedSet([1, 2, 3])
        b: PySortedSet = PySortedSet([1, 4])
        self.assertEquals(a & b, {1})
        b.add(3)
        self.assertEquals(a & b, {1, 3})
        a.remove(1)
        self.assertEquals(a & b, {3})

    def test_difference(self):
        a: PySortedSet = PySortedSet([1, 2, 3])
        b: PySortedSet = PySortedSet([1, 4])
        self.assertEquals(a - b, {2, 3})
        b.add(3)
        self.assertEquals(a - b, {2})
        a.remove(1)
        self.assertEquals(a - b, {2})

    def test_union(self):
        a: PySortedSet = PySortedSet([1, 2, 3])
        b: PySortedSet = PySortedSet([1, 4])
        self.assertEquals(a + b, {1, 2, 3, 4})
        b.add(5)
        self.assertEquals(a + b, {1, 2, 3, 4, 5})
        a.remove(1)
        self.assertEquals(a + b, {1, 2, 3, 4, 5})
        b.remove(4)
        self.assertEquals(a + b, {1, 2, 3, 5})

    def test_get_item(self):
        a: PySortedSet = PySortedSet([1, 2, 3, 5])
        self.assertEquals(a[0], 1)
        self.assertEquals(a[1], 2)
        self.assertEquals(a[2], 3)
        self.assertEquals(a[3], 5)
        a.add(4)
        self.assertEquals(a[0], 1)
        self.assertEquals(a[1], 2)
        self.assertEquals(a[2], 3)
        self.assertEquals(a[3], 4)
        self.assertEquals(a[4], 5)
        a.remove(2)
        self.assertEquals(a[0], 1)
        self.assertEquals(a[1], 3)
        self.assertEquals(a[2], 4)
        self.assertEquals(a[3], 5)

    def test_set_item(self):
        a: PySortedSet = PySortedSet([1, 2, 3, 5])
        self.assertEquals(a[0], 1)
        self.assertEquals(a[1], 2)
        self.assertEquals(a[2], 3)
        self.assertEquals(a[3], 5)
        a[2] = 4
        self.assertEquals(a[0], 1)
        self.assertEquals(a[1], 2)
        self.assertEquals(a[2], 4)
        self.assertEquals(a[3], 5)
        a[1] = 7
        self.assertEquals(a[0], 1)
        self.assertEquals(a[1], 4)
        self.assertEquals(a[2], 5)
        self.assertEquals(a[3], 7)
        a.remove(5)
        self.assertEquals(a[0], 1)
        self.assertEquals(a[1], 4)
        self.assertEquals(a[2], 7)
        a[0] = 8
        self.assertEquals(a[0], 4)
        self.assertEquals(a[1], 7)
        self.assertEquals(a[2], 8)


if __name__ == '__main__':
    unittest.main()
