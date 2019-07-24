from itertools import count
import sys
from suffix_tree.tree_builder import TreeBuilder
from suffix_tree.visitor.visitor import NodeDFS, DepthVisitor
from suffix_tree.suffix_tree import SuffixTree
from suffix_tree.node import Node
from suffix_tree.node_store import NodeStorePersist
import random
import string
import time

def ptime(s, t1, t2):
    diff = t2 - t1
    print("{} in {} ms".format(s, int(diff*1000)))

def depth_visit(nodeStore, startNode, final_offset):
    depth_visitor = DepthVisitor(final_offset)
    dfs = NodeDFS()
    dfs(depth_visitor, nodeStore, startNode)

t1 = time.time()
random.seed(3)
testcount = 0
number_tests = 100

def test_sequence(data, testcount, rlen):

    builder = TreeBuilder(data)
    builder.process_all_values()
    depth_visit(builder.nodeStore, builder.root, builder.last_offset)
    tree = SuffixTree(builder.root, builder.nodeStore, builder.dataSource)

    s = builder.dataSource
    print(f"S={s}")
    for substrlen in range(1, rlen+1):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.dataSource[start_offset:end_offset+1]
            #print(f"test_str='{test_str}'")

            result = tree.find(test_str)
            expected_result = tree.find_in_str(test_str, s)
            #print(f"{test_str}, {start_offset}, expected: {expected_result}, got: {result}")
            assert(start_offset in result)
            testcount += 1
    for substrlen in range(1, rlen):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.dataSource[start_offset: end_offset + 1] + "z"
            result = tree.find(test_str)
            assert(len(result) == 0)
            testcount += 1
    return testcount

test_len = 0
if len(sys.argv) > 1:
    test_len = int(sys.argv[1])
#test_str = "fbfceee"#a"#f"#f"#b"#f"#e" #None #"ddaaeeadfececeb"
#test_str = "eeee"
#test_str = "fbfceeea"
#test_str = "fbfceee"
#test_str = "feee"
#test_str = "fbfceeea"
test_str = None#'acbacbdaaccaacc'

class SearchPersist:
    def __init__(self, filePath):
        self.filePath = filePath

    def persist(self, searchString, startOffset):
        self.startOffset = startOffset
        with open(self.filePath, "w") as outputFile:
            outputFile.write(searchString)
            outputFile.write(f"{searchString}\n{startOffset}\n")

    def verify(self, result):
        if len(result) == 1 and result[0] == self.startOffset:
            with open(self.filePath, "a") as outputFile:
                outputFile.write(f"{result}, PASSES TEST\n")
        else:
            with open(self.filePath, "a") as outputFile:
                outputFile.write(f"Unexpected result: {result}\n")

if test_str:
    print(f"test_str={test_str}")
    testcount = test_sequence(test_str, testcount, len(test_str))
# length tests

elif test_len > 0:
    print(f"Test random tree, length {test_len}")
    data = ''.join(random.choice("ACGT") for i in range(test_len))
    builder = TreeBuilder(data)
    builder.process_all_values()

    testcount = 0
    tree = SuffixTree(builder.root, builder.nodeStore, builder.dataSource)
    tree.apply(DepthVisitor(builder.last_offset))

    # select a substring from data source, assume data source > 10000 values
    startOffset = random.randint(1000,3000)
    endOffset = random.randint(4000, 5000)
    searchString = data[startOffset:endOffset]
    print(f"{startOffset}-{endOffset}, {searchString[0:50]}...")
    result = tree.find(searchString)
    print(f"result={result}")
    searchPersister = SearchPersist("searchPersist.txt")
    searchPersister.persist(searchString,startOffset)
    searchPersister.verify(result)
    nodeStorePersist = NodeStorePersist("nodePersist.txt")
    nodeStorePersist.persist(builder.nodeStore)
else:
    for rlen in range(1,(number_tests+1)):
        print(rlen)
        data = (random.choice(string.ascii_letters[0:6]) for _ in range(rlen))
        data_as_str = ''.join(data)
        testcount = test_sequence(data_as_str, testcount, rlen)

t2 = time.time()
ptime(f"Completed {testcount} tests, created {Node.count} nodes", t1, t2)