from random import randint
from suffix_tree.node import ROOT
from suffix_tree.location import Location
from suffix_tree.traverser import Traverser
from suffix_tree.visitor.visitor import SuffixCollector, NodeDFS
import re

def tree_find(nodeStore, dataSource, test_str):
    location = Location()
    root = nodeStore.getNode(ROOT)
    location.locateOnNode(root)
    traverser = Traverser(nodeStore, dataSource)
    print(f"tree_find '{test_str}' in '{dataSource}'")
    # debug_on(True)
    debug_print(location)
    for value in test_str:
        if traverser.canFollowValue(location, value):
            print(f"Following value {value}")
            traverser.followValue(location, value)
            debug_print(location)
        else:
            debug_print(f"Cannot follow value {value} from {location}")
            break
    debug_print(f"FINAL: {location}")
    debug_print(nodeStore)
    suffixCollector = SuffixCollector()
    dfs = NodeDFS()
    dfs(suffixCollector, nodeStore, location.node)
    return suffixCollector.suffixes

global_debug = False

def debug_on(debugFlag):
    global global_debug
    global_debug = debugFlag

def debug_print(s):
    if global_debug:
        print(s)

def verify_tree(nodeStore, dataSource):
    dataLen = len(dataSource)
    startOffset = randint(0, dataLen - 1)
    endOffset = randint(startOffset+1, dataLen)
    test_str = dataSource[startOffset:endOffset]

    debug_print(f"{dataSource}[{startOffset}:{endOffset}] = {test_str}")

    # find all locations using regular expressions
    expected_locations = [m.start() for m in re.finditer(f"(?={test_str})", dataSource)]
    print(f"FIND '{test_str}' in '{dataSource}'")
    print(f"  EXPECTED: {expected_locations}")

    # find all locations using suffix tree representation
    actual_locations = tree_find(nodeStore, dataSource, test_str)
    print(f"  ACTUAL:   {actual_locations}")