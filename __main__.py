import sys

import time

from suffix_tree.node_factory import NodeFactory
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.suffix_tree import TreeBuilder
from suffix_tree.visitor.visitor import LeafCountVisitor, NodeDFS, DepthVisitor

def ptime(s, t1, t2):
    diff = t2 - t1
    print("{}={}".format(s, int(diff*1000)))

data = open(sys.argv[1], "r").read()
data2 = data[:1000000]
builder = TreeBuilder((c for c in data2))
t1 = time.time()
builder.process_all_values()
root_node = builder.root
t2 = time.time()
ptime("time to build tree", t1,t2)
number_nodes = builder.node_factory.final_id()
leaf_count_visitor = LeafCountVisitor(number_nodes)
depth_visitor = DepthVisitor()

dfs = NodeDFS()
t3 = time.time()
ptime("time to set up", t2,t3)
dfs(leaf_count_visitor, root_node)
t4 = time.time()
ptime("time to get leaf counts", t3,t4)
dfs(depth_visitor, root_node, number_nodes)
t5 = time.time()
ptime("time to get depth counts", t4,t5)
ptime("TOTAL", t1, t5)