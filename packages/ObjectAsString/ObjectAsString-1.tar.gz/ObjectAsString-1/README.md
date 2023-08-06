# ObjectAsString

ObjectAsString a library which makes coding in Python feel like Java and JavaScript. "+" operator will 
automatically be string concatenation if non-numeric types are involved.

# Installation

pip install ObjectAsString

# Usage

To use the library install it using the command shown in "Installation" section. 
Then, read the instructions below regarding how to use operations with StaticTypedList.

# Length

'len()' function can be called with a ObjectAsString as the parameter. It gets the length of the object in 
ObjectAsString if the object is either a list or a string.

Input: len(ObjectAsString([4, 5, 3])) 
Output: 3

# Addition

Adding two objects which are lists will be treated as combining lists. If two numbers are added, they will be treated
as addition of their values. Other additions will be considered string concatenation.

Input: ObjectAsString("5xf") + 2
Output: ObjectAsString("5xf2")

# Subtraction

Subtraction works between two objects which are numbers.

Input: ObjectAsString(mpf("5.3")) - mpf("2")
Output: ObjectAsString(mpf("3.3"))

# Multiplication

Multiplying a list and a number will be treated as repeating a list. Meanwhile, multiplying two numbers will be treated 
as multiplication of their values. Other

Input: ObjectAsString([4, 5, 3]) * 2
Output: [4, 5, 3, 4, 5, 3]

# Division

Division works between two objects which are numbers.

Input: ObjectAsString(mpf("5")) / mpf("2")
Output: ObjectAsString(mpf("2.5"))

# Modulo

Modulo works between two objects which are numbers.

Input: ObjectAsString(mpf("5")) % mpf("2")
Output: ObjectAsString(mpf("1"))

# Integer Division

Integer Division works between two objects which are numbers.

Input: ObjectAsString(5) // 2
Output: ObjectAsString(2)

# Exponents

Exponents work between two objects which are numbers.

Input: ObjectAsString(mpf("5")) ** mpf("2")
Output: ObjectAsString(mpf("25"))

# Comparisons

When applying comparisons (i.e., either '<', '<=', '>', '>=', '==', or '!='), two objects will be compared.

Input: ObjectAsString("ssd") == "ssd"
Output: True

# Tests

Tests for this project are available in 
https://github.com/DigitalCreativeApkDev/ObjectAsString/blob/master/ObjectAsString/ObjectAsString_tests.py.
