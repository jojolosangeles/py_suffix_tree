from suffix_tree.data_store import file_chars_with_offset, MmapDataStore
from suffix_tree.node import NodeFlattener
from suffix_tree.node_factory import NodeFactory
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.suffix_tree import TreeBuilder
from suffix_tree.visitor.visitor import NodeDFS, NodeBFS, DepthVisitor, Flattener, LeafCountVisitor, ComboVisitor


def depth_visit(tree):
    node = tree.root
    final_offset = tree.final_suffix
    depth_visitor = DepthVisitor()
    leaf_count_visitor = LeafCountVisitor()
    dfs = NodeDFS()
    dfs(ComboVisitor(depth_visitor,leaf_count_visitor), node, final_offset)

def test_setup():
    assert 4 == 4

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

if __name__ == "__main__":
    print("Running...")
    filePath = "/Users/jojo/genomes/python/chunked/h21_0.chunk"
    fcwo = file_chars_with_offset(filePath)
    builder = TreeBuilder(fcwo, MmapDataStore(filePath), NodeFactory(SuffixLinker()))
    print("process all values")
    builder.process_all_values()
    tree = builder.get_tree()
    print("visit all nodes")
    depth_visit(tree)
    print("done")