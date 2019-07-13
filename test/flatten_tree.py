from suffix_tree.data_store import file_chars_with_offset, MmapDataStore
from suffix_tree.node import NodeFlattener
from suffix_tree.node_factory import NodeFactory
from suffix_tree.persistence.flat_text import Flattener
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.suffix_tree import TreeBuilder
from suffix_tree.visitor.visitor import NodeDFS, NodeBFS, DepthVisitor, LeafCountVisitor, ComboVisitor
import sys
import time

def depth_visit(tree):
    node = tree.root
    final_offset = tree.final_suffix
    depth_visitor = DepthVisitor(final_offset)
    leaf_count_visitor = LeafCountVisitor()
    dfs = NodeDFS()
    dfs(ComboVisitor(depth_visitor,leaf_count_visitor), node)

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
    sys.setrecursionlimit(2000)
    if len(sys.argv) != 3:
        print("Usage: python flatten_tree.py <file_path> <output_extension>")
        exit()
    start_time = time.time()
    file_path = sys.argv[1]
    output_extension = sys.argv[2]
    fcwo = file_chars_with_offset(file_path)
    builder = TreeBuilder(fcwo, MmapDataStore(file_path), NodeFactory(SuffixLinker()))
    print("Building tree...")
    builder.process_all_values()
    tree_build_complete_time = time.time()
    tree = builder.get_tree()
    print("Traversing tree")
    depth_visit(tree)
    traversal_complete_time = time.time()
    print("Flattening tree")
    with open("{file_path}.{output_extension}".format(file_path=file_path,
                                                      output_extension = output_extension), "w") \
            as flat_tree, \
         open("{file_path}.{output_extension}".format(file_path=file_path,
                                                      output_extension = "dict"), "w") \
            as flat_dict:
        flattener = Flattener(tree.data_store, NodeFlattener(flat_tree), flat_dict)
        bfs = NodeBFS()
        bfs(flattener, tree.root)
    flatten_complete_time = time.time()
    print("Total time: {total:.2f}, tree built: {build_time:.2f}, traversed: {traversal_time}, flattened: {flatten_time}"
          .format(total=flatten_complete_time - start_time,
                  build_time=tree_build_complete_time-start_time,
                  traversal_time=traversal_complete_time-tree_build_complete_time,
                  flatten_time=flatten_complete_time-tree_build_complete_time))