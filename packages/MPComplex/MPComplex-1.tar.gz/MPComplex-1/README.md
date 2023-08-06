# MPComplex

MPComplex is a data type which support complex numbers which allow comparison and sorting operations. This library 
extends 'mpc' in 'mpmath' library (https://pypi.org/project/mpmath/) by allowing comparisons and sorting.

## MPComplex Operations

The operations supported by MPComplex are addition, subtraction, multiplication, division, power, comparisons, and 
sorting.

## Addition

Input: MPComplex(4, 2) + MPComplex(5, 3)
Output: MPComplex(9, 5)

## Subtraction

Input: MPComplex(7, 9) - MPComplex(3, 3)
Output: MPComplex(4, 6)

## Multiplication

Input: MPComplex(5, 4) * MPComplex(4, 6)
Output: MPComplex(-4, 46)

## Division

Input: MPComplex(5, 4) / MPComplex(4, 6)
Output: MPComplex(0.846153846153846, -0.269230769230769)

## Power

Input: MPComplex(4, 2) ** 5
Output: MPComplex(-1216, 1312)

## Comparisons in General

MPComplex objects are compared to each other in the following order:

1. real part value
2. imaginary part value

For example, to check whether MPComplex object a is greater than MPComplex object b or not, the program 
does the following steps:

1. Checks if the real part of a is greater than the real part of b or not. If yes, 'True' is returned.
2. If the real part of a is equal to the real part of b, go to step 3. Else, go to step 4.
3. Return true if the imaginary part of a is greater than the imaginary part of b. Else, return 'False'.
4. Return 'False' immediately.

The similar process applies to the operations 'less than', 'less than or equal to', and 'greater than or equal to'
as well.

For checking equality of two complex numbers, equality applies if the real and imaginary parts of both numbers are
equal.

### Greater Than

Input: MPComplex(5, 4) > MPComplex(4, 6)
Output: True

### Greater Than or Equal To

Input: MPComplex(5, 4) >= MPComplex(4, 6)
Output: True

### Less Than

Input: MPComplex(5, 4) < MPComplex(4, 6)
Output: False

### Less Than or Equal To

Input: MPComplex(5, 4) <= MPComplex(4, 6)
Output: False

### Equal To

Input: MPComplex(4, 2) == MPComplex(4, 1)
Output: False

### Not Equal To

Input: MPComplex(4, 2) != MPComplex(4, 1)
Output: True

## Sorting

If a list of MPComplex objects is called with sort() method, the list will be sorted in ascending order.

Input: [MPComplex(4, 2), MPComplex(4, 1), MPComplex(5, 3), MPComplex(2, 7)].sort()
Output: [MPComplex(2, 7), MPComplex(4, 1), MPComplex(4, 2), MPComplex(5, 3)]
