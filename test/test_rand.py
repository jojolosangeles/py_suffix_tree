from itertools import count

from suffix_tree.location import LocationFactory
from suffix_tree.node_factory import NodeFactory
from suffix_tree.relocate import Relocate
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.suffix_tree import TreeBuilder
from suffix_tree.visitor.visitor import LeafCountVisitor, NodeDFS, PrintVisitor, DepthVisitor, SuffixCollector
import random
import string

def find(str, node, data_store):
    location = LocationFactory.create(node)
    mover = Relocate(data_store)
    for x in str:
        location, found_value = mover.follow_value(location, x)
        if not found_value:
            raise ValueError("Did not find {} in {}".format(x, str))
    suffix_collector = SuffixCollector()
    nodeDFS = NodeDFS()
    nodeDFS(suffix_collector, location.node)
    return suffix_collector.suffixes

random.seed(3)
for rlen in range(1,100):
    data = (random.choice(string.ascii_letters[0:6]) for _ in range(rlen))
    suffix_linker = SuffixLinker()
    builder = TreeBuilder(data, NodeFactory(suffix_linker))
    builder.process_all_values()
    s = builder.data_store.value_str(0, rlen)
    #print("S={}".format(s))
    print(rlen)
    for substrlen in range(1, rlen+1):
        for start_offset,end_offset in zip(count(), range(substrlen-1, rlen)):
            test_str = builder.data_store.value_str(start_offset, end_offset)
            #print("test_str={}".format(test_str))
            result = find(test_str, builder.root, builder.data_store)
            assert(start_offset in result)


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