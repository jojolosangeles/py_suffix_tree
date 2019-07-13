import sys
import ast

if len(sys.argv) != 2:
    print("Usage: python loc2csv.py <locfile>")
    exit()

class LocFile:
    def __init__(self, filePath):
        data = filePath.split("/")
        fileName = data[-1]
        fData = fileName.split(".")
        sfData = fData[0].split("_")
        millionOffset = int(sfData[-1])
        self.offset = millionOffset*1000000

class LocLine:
    def __init__(self, baseOffset):
        self.baseOffset = baseOffset

    def process(self, line):
        data = line.split(" ", 1)
        sequence = data[0]
        sequence_length = len(sequence)
        locations = ast.literal_eval(data[1])
        locations = [ n + self.baseOffset for n in locations]
        for loc in locations:
            print("{sequence},{sequence_length},{location}"
                  .format(sequence=sequence,sequence_length=sequence_length,location=loc))

locFilePath = sys.argv[1]
locFile = LocFile(locFilePath)
locLine = LocLine(locFile.offset)
with open(locFilePath, "r") as lfp:
    for line in lfp:
        locLine.process(line.strip())
