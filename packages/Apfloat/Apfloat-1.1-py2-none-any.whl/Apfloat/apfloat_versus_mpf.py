# Importing necessary libraries


from apfloat import *
from timeit import default_timer as timer


def main():
    # Creating the file to store data of tests.

    tests_data_file = open("Apfloat_versus_mpf.txt", "w+")
    tests_data_file.write("Test Number, Apfloat, mpf\n")

    # Implementing 100 tests.

    for i in range(100):
        # Test: Adding 10000 BigNumber objects to a list

        # a. Using BigNumber
        start1 = timer()
        a_list: list = []  # initial value
        for j in range(10000):
            a_list.append(Apfloat(j))

        end1 = timer()

        # b. Using mpf
        start2 = timer()
        a_list: list = []  # initial value
        for j in range(10000):
            a_list.append(mpf(j))

        end2 = timer()
        Apfloat_time = end1 - start1
        mpf_time = end2 - start2
        tests_data_file.write(str(i + 1) + ", " + str(Apfloat_time) + " seconds, " + str(mpf_time) + " seconds\n")


if __name__ == '__main__':
    main()
