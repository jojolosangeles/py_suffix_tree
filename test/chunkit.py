import sys

if len(sys.argv) != 4:
    print("Usage: python chunkit.py <filePath> <short_name> <chunk_size>")
    exit()

filePath = sys.argv[1]
shortName = sys.argv[2]
chunkSize = int(sys.argv[3])

offset = 0
with open(filePath, "r") as fp:
    data = fp.read(chunkSize)
    while len(data) > 0:
        data = data.replace("N","")
        outputFileName = "{}_{}.chunk".format(shortName, offset)
        print(outputFileName)
        with open(outputFileName, "w") as out_fp:
            out_fp.write(data)
        offset += 1
        data = fp.read(chunkSize)
