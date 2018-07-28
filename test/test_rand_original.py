from itertools import count

from suffix_tree.location import Location
from suffix_tree.suffix_tree import TreeBuilder
from suffix_tree.visitor.visitor import NodeDFS, SuffixCollector
import random
import string
import time

def find(str, node, data_store):
    location = Location(node, data_store)
    for x in str:
        found_value = location.follow_value(x)
        if not found_value:
            raise ValueError("Did not find {} in {}".format(x, str))
    suffix_collector = SuffixCollector()
    nodeDFS = NodeDFS()
    nodeDFS(suffix_collector, location.ending_node())
    return suffix_collector.suffixes

def ptime(s, t1, t2):
    diff = t2 - t1
    print("{} in {} ms".format(s, int(diff*1000)))

t1 = time.time()
random.seed(3)
testcount = 0
for rlen in range(1,50):
    print(rlen)
    data = (random.choice(string.ascii_letters[0:6]) for _ in range(rlen))
    builder = TreeBuilder(data)
    builder.process_all_values()
    s = builder.data_store.value_str(0, rlen)
    print("S={}".format(s))
    for substrlen in range(1, rlen+1):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.data_store.value_str(start_offset, end_offset)
            result = find(test_str, builder.root, builder.data_store)
            assert(start_offset in result)
            testcount += 1
    for substrlen in range(1, rlen):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.data_store.value_str(start_offset, end_offset) + "z"
            try:
                result = find(test_str, builder.root, builder.data_store)
                assert(False)
            except ValueError:
                testcount += 1

t2 = time.time()
ptime("Completed {} tests".format(testcount), t1, t2)