from itertools import count

from suffix_tree_igraph.location import LocationFactory, Location
from suffix_tree_igraph.node_factory import NodeFactory
from suffix_tree_igraph.relocate import Relocate
from suffix_tree_igraph.suffix_linker import SuffixLinker
from suffix_tree_igraph.suffix_tree import TreeBuilder
from suffix_tree_igraph.visitor.visitor import NodeDFS, SuffixCollector
import random
import string
from suffix_tree_igraph.igraph_adapter import igraph_print_tree, igraph_reset, igraph_instance


def find(str, node_id, data_store, node_factory):
    location = Location(node_id, Location.ON_NODE)
    location = LocationFactory.create_on_node(location, node_id)
    mover = Relocate(data_store, node_factory)
    for x in str:
        location, found_value = mover.follow_value(location, x)
        if not found_value:
            raise ValueError("Did not find {} in {}".format(x, str))
    suffix_collector = SuffixCollector()
    nodeDFS = NodeDFS(igraph_instance(), node_factory)
    nodeDFS(suffix_collector, location.node_id)
    return suffix_collector.suffixes

random.seed(3)
testcount = 0
for rlen in range(1,30):
    print("TEST {}".format(rlen))
    igraph_reset()
    data = (random.choice(string.ascii_letters[0:6]) for _ in range(rlen))
    suffix_linker = SuffixLinker()
    builder = TreeBuilder(data, NodeFactory(suffix_linker))
    builder.process_all_values()
    s = builder.data_store.value_str(0, rlen)
    print("S={}".format(s))
    for substrlen in range(1, rlen+1):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.data_store.value_str(start_offset, end_offset)
            result = find(test_str, builder.root_id, builder.data_store, builder.node_factory)
            assert(start_offset in result)
            testcount += 1
    for substrlen in range(1, rlen+1):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.data_store.value_str(start_offset, end_offset) + "z"
            try:
                result = find(test_str, builder.root_id, builder.data_store, builder.node_factory)
            except ValueError:
                testcount += 1


print("Completed {} tests".format(testcount))

"""
suffix_linker = SuffixLinker()
data = open("./test.txt", "r").read()
builder = TreeBuilder((c for c in data), NodeFactory(suffix_linker))
builder.process_all_values()
root_node = builder.root

leaf_count_visitor = LeafCountVisitor(builder.final_id())
depth_visitor = DepthVisitor()

dfs = NodeDFS()
dfs(leaf_count_visitor, root_node)
dfs(depth_visitor, root_node, builder.node_factory.final_id())

pv = PrintVisitor()
dfs(pv, root_node)"""