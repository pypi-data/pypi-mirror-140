# Importing necessary libraries


import random
from ObjectAsString import *
from timeit import default_timer as timer


def generate_random_string() -> str:
    res: str = ""  # initial value
    for i in range(random.randint(6, 10)):
        letters: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        res += letters[random.randint(0, len(letters) - 1)]

    return res


def main():
    # Creating the file to store data of tests.

    tests_append_data_file = open("ObjectAsString_versus_list_append.txt", "w+")
    tests_append_data_file.write("Test Number, ObjectAsString, list\n")
    tests_sort_data_file = open("ObjectAsString_versus_list_sort.txt", "w+")
    tests_sort_data_file.write("Test Number, ObjectAsString, list\n")

    # Implementing 100 tests

    for i in range(100):
        # Test 1: Appending 100 strings of length 6 to 10 to a list

        # a. Using ObjectAsString
        start1 = timer()
        a_list: list = []  # initial value
        for j in range(100):
            a_list.append(ObjectAsString(generate_random_string()))

        end1 = timer()

        # b. Using string
        start2 = timer()
        b_list: list = []  # initial value
        for j in range(100):
            b_list.append(generate_random_string())

        end2 = timer()
        ObjectAsString_time = end1 - start1
        string_time = end2 - start2
        tests_append_data_file.write(str(i + 1) + ", " + str(ObjectAsString_time) + " seconds, " + str(string_time) +
                                     " seconds\n")

        # Test 2: Sorting 100 strings in both lists

        # a. Using ObjectAsString
        start3 = timer()
        a_list: list = []  # initial value
        for j in range(100):
            a_list.append(ObjectAsString(generate_random_string()))

        a_list.sort()
        end3 = timer()

        # b. Using string
        start4 = timer()
        b_list: list = []  # initial value
        for j in range(100):
            b_list.append(generate_random_string())

        b_list.sort()
        end4 = timer()
        ObjectAsString_time = end3 - start3
        string_time = end4 - start4
        tests_sort_data_file.write(str(i + 1) + ", " + str(ObjectAsString_time) + " seconds, " + str(string_time) +
                                   " seconds\n")


if __name__ == '__main__':
    main()
