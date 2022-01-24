

import os

import numpy


def sroot(number):
    if number > 0:
        value = numpy.sqrt(number)
    else:
        value = 'Not real'
    return value


print('Running cartons.py script in ' + str(os.getcwd()))
