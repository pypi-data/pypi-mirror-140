# Importing necessary libraries


from PySortedSet import *
from timeit import default_timer as timer
from mpmath import mpf, mp
mp.pretty = True


def main():
    # Creating the file to store data of tests.

    tests_data_file = open("PySortedSet_versus_set.txt", "w+")
    tests_data_file.write("Test Number, PySortedSet, set\n")

    # Implementing 100 tests

    for i in range(100):
        # Test: Adding 100 numbers to a PySortedSet and a set

        # a. Using PySortedSet
        start1 = timer()
        py_sorted_set: PySortedSet = PySortedSet()
        for j in range(100):
            py_sorted_set.add(mpf(j))

        end1 = timer()

        # b. Using set
        start2 = timer()
        a_set: set = set()
        for j in range(100):
            a_set.add(mpf(j))

        end2 = timer()
        PySortedSet_time = end1 - start1
        set_time = end2 - start2
        tests_data_file.write(str(i + 1) + ", " + str(PySortedSet_time) + " seconds, " + str(set_time) + " seconds\n")


if __name__ == '__main__':
    main()
