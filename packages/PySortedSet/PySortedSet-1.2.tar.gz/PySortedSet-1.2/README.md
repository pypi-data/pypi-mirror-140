# PySortedSet

PySortedSet is a data type supporting a sorted set which is aware of indices.

# Installation

pip install PySortedSet

# Usage

To use the library install it using the command shown in "Installation" section. 
Then, read the instructions below regarding how to use operations with Apfloat.

## Length

'len()' function can be called with a PySortedSet as the parameter. It gets the number of elements in the PySortedSet. 

Input: len(PySortedSet([1, 4, 5]))
Output: 3

## Contains

Input: 5 in PySortedSet([5, 6, 2])
Output: True

## Union

Input: PySortedSet([5, 6, 2]) + PySortedSet([5, 3])
Output: PySortedSet([2, 3, 5, 6])

## Intersection

Input: PySortedSet([5, 6, 2]) & PySortedSet([5, 3])
Output: PySortedSet([5])

## Difference

Input: PySortedSet([5, 6, 2]) - PySortedSet([5, 3])
Output: PySortedSet([6, 2])

## Get Element at Index

Input: 

a: PySortedSet = PySortedSet([5, 6, 2])
print(a[2])

Output: 6

## Set Element at Index

Input: 

a: PySortedSet = PySortedSet([5, 6, 2])
a[2] = 1
print(a)

Output: {1, 2, 5}

## Add Element

Input: 

a: PySortedSet = PySortedSet([5, 6, 2])
a.add(1)
print(a)

Output: {1, 2, 5, 6}

## Remove Element

Input: 

a: PySortedSet = PySortedSet([5, 6, 2])
a.remove(5)
print(a)

Output: {2, 6}

## Pop Element

a: PySortedSet = PySortedSet([5, 6, 2])
a.pop(0)
print(a)

Output: {5, 6}

## Checking for Equality

Input: PySortedSet([5, 6, 2]) == {2, 5, 6}
Output: True
