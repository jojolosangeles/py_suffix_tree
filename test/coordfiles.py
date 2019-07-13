import glob
import os
import sys

folder = sys.argv[1]
dimensions = int(sys.argv[2])

files = sorted(glob.glob("{}/*.x".format(folder)))
for f in files:
    print(f)