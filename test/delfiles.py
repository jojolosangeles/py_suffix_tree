import glob
import os
import sys

folder = sys.argv[1]
line_limit = int(sys.argv[2])

files = glob.glob("{}/*.x".format(folder))
for f in files:
    number_lines = 0
    with open(f, "r") as infile:
        number_lines = len(infile.readlines())
    if number_lines <= line_limit:
        os.remove(f)
