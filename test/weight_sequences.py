import sys

from suffix_tree.data_store import MmapDataStore

if len(sys.argv) != 4:
    print("Usage: python weight_sequences.py <dict_file> <sequence_min_length> <key_weight_output_file>")
    exit()

dict_file = sys.argv[1]
sequence_min_length = int(sys.argv[2])
key_weight_output_file = "{}.{}".format(dict_file,sys.argv[3])

with open(dict_file, "r") as input_file:
    with open(key_weight_output_file, "w") as output_file:
        for line in input_file:
            data = line.split("'")
            if len(data) == 3:
                if len(data[1]) > sequence_min_length and len(data[1]) < MmapDataStore.MAX_READ_SIZE:
                    id = data[0].split(' ')[0]
                    sequence = data[1]
                    weight = len(data[1]) - sequence_min_length
                    output_file.write("{} {} {}\n".format(id, sequence, weight))
