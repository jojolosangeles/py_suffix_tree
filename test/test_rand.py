from itertools import count

from suffix_tree_igraph.location import LocationFactory, Location
from suffix_tree_igraph.relocate import Relocate
from suffix_tree_igraph.suffix_tree import TreeBuilder
from suffix_tree_igraph.visitor.visitor import NodeDFS, SuffixCollector
import random
import string


def find(str, node_id, data_store, tree_graph):
    location = Location(node_id)
    location = LocationFactory.create_on_node(location, node_id, location.start_offset, location.end_offset)
    mover = Relocate(data_store, tree_graph)
    for x in str:
        location, found_value = mover.follow_value(location, x)
        if not found_value:
            raise ValueError("Did not find {} in {}".format(x, str))
    suffix_collector = SuffixCollector(tree_graph)
    nodeDFS = NodeDFS(tree_graph.strategy.g)
    nodeDFS(suffix_collector, location.node_id)
    return suffix_collector.suffixes

random.seed(3)
testcount = 0
for rlen in range(1,50):
    print("TEST {}".format(rlen))
    data = (random.choice(string.ascii_letters[0:6]) for _ in range(rlen))
    builder = TreeBuilder(data)
    builder.process_all_values()
    tree_graph = builder.tree_graph
    s = builder.data_store.value_str(0, rlen)
    print("S={}".format(s))
    for substrlen in range(1, rlen+1):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.data_store.value_str(start_offset, end_offset)
            result = find(test_str, tree_graph.root, builder.data_store, builder.tree_graph)
            assert(start_offset in result)
            testcount += 1
    for substrlen in range(1, rlen):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.data_store.value_str(start_offset, end_offset) + "z"
            try:
                result = find(test_str, tree_graph.root, builder.data_store, builder.tree_graph)
                assert(False)
            except ValueError:
                testcount += 1

print("Completed {} tests".format(testcount))
