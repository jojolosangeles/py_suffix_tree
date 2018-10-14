from suffix_tree.node_factory import NodeFactory
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.suffix_tree import TreeBuilder
from suffix_tree.visitor.visitor import LeafCountVisitor, NodeDFS, PrintVisitor, DepthVisitor
import os

suffix_linker = SuffixLinker()
data = open("{script_path}/test/test.txt".format(script_path=os.environ['PYTHONPATH']), "r").read()
builder = TreeBuilder((c for c in data), NodeFactory(suffix_linker))
builder.process_all_values()
root_node = builder.root

leaf_count_visitor = LeafCountVisitor(builder.final_id())
depth_visitor = DepthVisitor()

dfs = NodeDFS()
dfs(leaf_count_visitor, root_node)
dfs(depth_visitor, root_node, builder.final_id())

pv = PrintVisitor()
dfs(pv, root_node)

