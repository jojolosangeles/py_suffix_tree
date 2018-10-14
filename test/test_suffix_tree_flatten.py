from suffix_tree.node import NodeFlattener
from suffix_tree.node_factory import NodeFactory
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.suffix_tree import TreeBuilder
from suffix_tree.visitor.visitor import NodeDFS, NodeBFS, DepthVisitor, Flattener


def depth_visit(tree):
    node = tree.root
    final_offset = tree.final_suffix
    depth_visitor = DepthVisitor()
    dfs = NodeDFS()
    dfs(depth_visitor, node, final_offset)

def func(x):
    return x + 1

def test_setup():
    assert func(3) == 4

def test_create_tree():
    data = "abc"
    builder = TreeBuilder(data, NodeFactory(SuffixLinker()))
    builder.process_all_values()
    tree = builder.get_tree()
    depth_visit(tree)
    assert tree is not None

def test_flatten_tree():
    data = "mississippi"
    builder = TreeBuilder(data, NodeFactory(SuffixLinker()))
    builder.process_all_values()
    tree = builder.get_tree()
    depth_visit(tree)
    with open("mississippi.flat", "w") as flat_tree, open("mississippi.dict", "w") as flat_dict:
        flattener = Flattener(tree.data_store, NodeFlattener(flat_tree), flat_dict)
        bfs = NodeBFS()
        bfs(flattener, tree.root)

test_flatten_tree()