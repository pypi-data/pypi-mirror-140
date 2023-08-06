# Importing necessary libraries


from StaticTypedList import *
from timeit import default_timer as timer
from mpmath import mpf, mp
mp.pretty = True


def main():
    # Creating the file to store data of tests.

    tests_append_data_file = open("StaticTypedList_versus_list_append.txt", "w+")
    tests_append_data_file.write("Test Number, StaticTypedList, list\n")
    tests_sort_data_file = open("StaticTypedList_versus_list_sort.txt", "w+")
    tests_sort_data_file.write("Test Number, StaticTypedList, list\n")

    # Implementing 100 tests

    for i in range(100):
        # Test 1: Appending 100 numbers to a StaticTypedList and a list

        # a. Using StaticTypedList
        start1 = timer()
        static_typed_list: StaticTypedList = StaticTypedList()
        for j in range(100):
            static_typed_list.append(mpf(j))

        end1 = timer()

        # b. Using list
        start2 = timer()
        a_list: list = []
        for j in range(100):
            a_list.append(mpf(j))

        end2 = timer()
        StaticTypedList_time = end1 - start1
        list_time = end2 - start2
        tests_append_data_file.write(str(i + 1) + ", " + str(StaticTypedList_time) + " seconds, " + str(list_time) +
                              " seconds\n")

        # Test 2: Sorting 100 numbers to a StaticTypedList and a list

        # a. Using StaticTypedList
        start3 = timer()
        static_typed_list: StaticTypedList = StaticTypedList()
        for j in range(100):
            static_typed_list.append(mpf(j))

        static_typed_list.sort()
        end3 = timer()

        # b. Using list
        start4 = timer()
        a_list: list = []
        for j in range(100):
            a_list.append(mpf(j))

        a_list.sort()
        end4 = timer()
        StaticTypedList_time = end3 - start3
        list_time = end4 - start4
        tests_sort_data_file.write(str(i + 1) + ", " + str(StaticTypedList_time) + " seconds, " + str(list_time) +
                                     " seconds\n")


if __name__ == '__main__':
    main()
