# Importing necessary libraries
from mp_complex import *
from mpmath import mp, mpc
mp.pretty = True
from timeit import default_timer as timer
import random


def main():
    # Creating the files to store data of tests.
    tests_append_data_file = open("mp_complex_versus_mpc_append.txt", "w+")
    tests_append_data_file.write("Test Number, MPComplex, mpc\n")

    # Implementing 100 tests
    for i in range(100):
        # Test: Adding 100 random complex numbers

        # a. Using MPComplex
        start_append1 = timer()
        a_list: list = []
        for k in range(100):
            a_list.append(MPComplex(random.random(), random.random()))

        end_append1 = timer()
        mp_complex_append_time = end_append1 - start_append1

        # b. Using mpc
        start_append2 = timer()
        b_list: list = []
        for k in range(100):
            b_list.append(mpc(random.random(), random.random()))

        end_append2 = timer()
        mpc_append_time = end_append2 - start_append2
        tests_append_data_file.write(str(i + 1) + ", " + str(mp_complex_append_time) + " seconds, " +
                                     str(mpc_append_time) + " seconds\n")


if __name__ == '__main__':
    main()
