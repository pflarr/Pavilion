#!/usr/bin/env python

import sys
import re
from optparse import OptionParser

"""
  Program to take two baseline data files and compare the corresponding
  data values for each unique test type.
  author: C. Idler, June, 2015
"""


# Initialize each data entry with its interesting values (min, max, etc.)
# example line:
# avg_aggregate_mem_scale_rate = 12492.00859375 (entries - 768, min - 12236.4, max - 12863.0, stDev - 115.182365386109)
class ResultLine():
    # class to extract data fields from result line
    def __init__(self, data_str):

        # my_name = self.__class__.__name__
        # print my_name + ": " + data_str,

        my_string = data_str.split()
        self.avg = my_string[2]

        m_min = re.match(".* min - (.*), max", data_str)
        if m_min:
            self.min = m_min.group(1)
            # print " save this min - " + self.min
        m_max = re.match(".* max - (.*), stDev", data_str)
        if m_max:
            self.max = m_max.group(1)
            # print " save this max - " + self.max
        m_std = re.match(".*stDev - (.*)\)", data_str)
        if m_std:
            self.std = m_std.group(1)


# calculate differentials of data in baseline results
def calc_diff(res1, res2):
    """
    :param res1: individual ResultLine from first file
    :param res2: individual ResultLine from second file
    :return: string showing percent differences between values
    """

    try:
        avg_diff = 100 * (float(res1.avg) - float(res2.avg)) / float(res1.avg)
    except ZeroDivisionError:
        avg_diff = 0
    avg_diff = abs(round(avg_diff, 1))

    try:
        min_diff = 100 * (float(res1.min) - float(res2.min)) / float(res1.min)
    except ZeroDivisionError:
        min_diff = 0
    min_diff = abs(round(min_diff, 1))

    try:
        max_diff = 100 * (float(res1.max) - float(res2.max)) / float(res1.max)
    except ZeroDivisionError:
        max_diff = 0
    max_diff = abs(round(max_diff, 1))

    try:
        std_diff = 100 * (float(res1.std) - float(res2.std)) / float(res1.std)
    except ZeroDivisionError:
        std_diff = 0
    std_diff = abs(round(std_diff, 1))

    return "mean - " + str(avg_diff) + "\tmin - " + str(min_diff) + "\tmax - " + str(max_diff) + "\tstdDev - "\
           + str(std_diff)


# read in each baseline data file as a dictionary keyed by test_type "name.num_nodesXnum_pes(args)"
def load_bl_file(name, opt):
    """
    :param name: input file name
    :param opt: command line options
    :return: dictionary with test_types as keys and values as a list of individual data lines
    """

    data_dict = dict()

    with open(name, 'r') as in_file:
        test_type = None
        for line in in_file:
            if opt.verbose:
                print "scan line -> " + line,
            if isinstance(line, str):
                m = re.match("(^.*\)):", line)
                # new key found
                if m:
                    test_type = m.group(1)
                    if opt.verbose:
                        print " * matched test type - " + line,
                # else, add each line (ignore empty lines) as elements of this latest key
                elif test_type:
                    if line.strip():
                        data_dict.setdefault(test_type, []).append(line)

    return data_dict

# -------------------------------------------------------------------------  #
# Main


def main():

    # parser adds help option and verbose mode
    usage = "usage: %prog [options] input-file1 input-file2"
    parser = OptionParser(usage=usage)
    parser.add_option("-v", action="store_true", dest="verbose", help="show data being consumed and matched")
    (options, args) = parser.parse_args()

    # Expect two files names of baseline data from Pavilion tests
    try:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
    except IndexError:
        print "Must be 2 input args, exiting!"
        exit()

    # Show a key as to what data line belongs to which input file
    print "\nComparing files:"
    print " file1 > " + sys.argv[1]
    print " file2 < " + sys.argv[2]
    print "\n ------------"

    # Read em in and make dictionaries
    file1_dict = load_bl_file(file1, options)
    file2_dict = load_bl_file(file2, options)
    print "\n ------------"

    # For each test_type compare like trend data vales to see any differences
    for k in file1_dict.keys():
        # If the second file does not have a like test_type, there is no reason to compare values.
        # If the first file does not have a matching test_type then it won't even exist to loop on.
        if k not in file2_dict:
            del (file1_dict[k])
            continue

        # stmt to help understand what is being picked off of the data line
        # print list([x.split(' ', 2)[1] for x in file1_dict[k] for y in file2_dict[k]])

        # Fold all the corresponding data lines together with this fancy iterable stmt
        merged_list = [(x, y) for x in file1_dict[k] for y in file2_dict[k] if x.split(' ', 2)[1] == y.split(' ', 2)[1]]

        # Display the results
        print "\n" + k + ":"
        for p1, p2 in merged_list:
            print "> " + p1,
            print "< " + p2,
            r1 = ResultLine(p1)
            r2 = ResultLine(p2)
            print "\t\tPercent Diffs : " + calc_diff(r1, r2) + "\n"

    # Tried this zip to fold the data lines together, but only does by position as far as I can tell, so
    # it potentially mixes up data lines if they are not in the correct order.
    # print "\n" + k + ":"
    # for v1, v2 in zip(file1_dict[k], file2_dict[k]):
    #   if isinstance(v1, str) and isinstance(v2, str) and (not v1.isspace()):
    #       print "> " + v1,
    #       print "< " + v2,
    #      r1 = ResultLine(v1)
    #      r2 = ResultLine(v2)
    #     print "\t\tPercent Diffs : " + calc_diff(r1, r2) + "\n"

if __name__ == "__main__":
    main()

