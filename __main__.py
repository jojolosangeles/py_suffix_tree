"""Executable suffix tree"""
import sys

from suffix_tree.node_factory import NodeFactory
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.suffix_tree import TreeBuilder, NodeStr

suffix_linker = SuffixLinker()
builder = TreeBuilder((c for c in "mississippi"), NodeFactory(suffix_linker))

"""
Build a tree from sequence 'mississippi'
                            01234567890

Nodes other than root have an incoming edge represented by an inclusive range
going from incoming_edge_start_offset to incoming_edge_end_offset.

Root has values (-1,-1) for this range.

Leaf has values (incoming_edge_start_offset, -1) for this range.

"""

class Verifier:
    def __init__(self, root, location):
        self.root = root
        self.location = location
        self.nodeState = {}
        self.set_state(None, (-1, -1))

    def set_state(self, k, v):
        self.nodeState[k] = v

    def replace_state(self, old_traversal, new_traversal):
        self.nodeState[new_traversal] = self.nodeState[old_traversal]
        self.nodeState.pop(old_traversal, None)

    def traverse_to(self, traversal):
        node = self.root
        if traversal != None:
            for key in list(traversal):
                node = node.children[key]
        return node

    def verify(self):
        for traversal in self.nodeState:
            self.verifyNode(traversal, self.traverse_to(traversal), *self.nodeState[traversal])

    def expect_equal(self, loc, traversal, expected, actual):
        if expected != actual:
            print("** FAIL {}: {} expected {}, got {}".format(loc, traversal, expected, actual))

    def verifyNode(self, traversal, node, start_offset, end_offset):
        self.expect_equal("node {} start after '{}'".format(node, traversal), traversal, start_offset, node.incoming_edge_start_offset)
        self.expect_equal("node {} end after '{}'".format(node, traversal), traversal, end_offset, node.incoming_edge_end_offset)

    def verifyLocation(self, traversal, on_node, value_offset):
        node = self.traverse_to(traversal)
        self.expect_equal("loc node after '{}'".format(traversal), traversal, node, self.location.node)
        self.expect_equal("loc on_node after '{}'".format(traversal), traversal, on_node, self.location.on_node)
        self.expect_equal("loc value_offset after '{}'".format(traversal), traversal, value_offset, self.location.data_offset)

def edge_with_loc(start_offset, value_offset, str):
    str_offset = value_offset - start_offset
    return "{}({}){}".format(str[:str_offset], str[str_offset:str_offset+1], str[str_offset+1:])
    #return "edge_with_loc {}, str_offset={}".format(str, str_offset)

nodestr = NodeStr(builder.data_store)
def size_of(node):
    return sys.getsizeof(node) + sum(list(map(lambda x: size_of(x), node.children.values())), 0)

def printTree(root):
    print(nodestr.tree_str(root))
    print("Location: {}, {}".format(nodestr.node_str(location.node), edge_with_loc(location.node.incoming_edge_start_offset, location.data_offset, nodestr.edge_str(location.node))))
    print("tree size={}".format(size_of(root)))

print("START TEST")
root = builder.root
location = builder.location

verifier = Verifier(root, location)
verifier.verify()
verifier.verifyLocation(None, True, -1)

print("..add 'm'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.set_state("m", (0, -1))
verifier.verify()
verifier.verifyLocation(None, True, -1)

print("..add 'i'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.set_state("i", (1, -1))
verifier.verify()
verifier.verifyLocation(None, True, -1)

print("..add 's'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.set_state("s", (2, -1))
verifier.verify()
verifier.verifyLocation(None, True, -1)

print("..add 's'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.verify()
verifier.verifyLocation("s", False, 2)

print("..add 'i'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("s", (2, 2))
verifier.set_state("ss", (3, -1))
verifier.verify()
verifier.verifyLocation("s", True, 2)

result = builder.process_value_at_location(value, offset)
assert(result == True)


verifier.set_state("si", (4, -1))
verifier.verify()
verifier.verifyLocation(None, True, -1)

result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.verify()
verifier.verifyLocation("i", False, 1)

print("..add 's'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.verify()
verifier.verifyLocation("i", False, 2)

print("..add 's'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.verify()
verifier.verifyLocation("i", False, 3)

print("..add 'i'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.verify()
verifier.verifyLocation("i", False, 4)

print("..add 'p'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("i", (1, 4))
verifier.set_state("is", (5, -1))
verifier.verify()
verifier.verifyLocation("i", True, 4)

result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("ip", (8, -1))
verifier.verify()
verifier.verifyLocation("ss", False, 4)

result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("ss", (3, 4))
verifier.set_state("sss", (5, -1))
verifier.verify()
verifier.verifyLocation("ss", True, 4)

result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("ssp", (8, -1))
verifier.verify()
verifier.verifyLocation("si", False, 4)

result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("si", (4, 4))
verifier.set_state("sis", (5, -1))
verifier.verify()
verifier.verifyLocation("si", True, 4)

result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("sip", (8, -1))
verifier.verify()
verifier.verifyLocation("i", False, 1)

result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.replace_state("is", "iss")
verifier.replace_state("ip", "isp")
verifier.set_state("i", (1, 1))
verifier.set_state("is", (2, 4))
verifier.verify()
verifier.verifyLocation("i", True, 1)

result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("ip", (8, -1))
verifier.verify()
verifier.verifyLocation(None, True, -1)

result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.set_state("p", (8, -1))
verifier.verify()
verifier.verifyLocation(None, True, -1)

print("..add 'p'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == False)

verifier.verify()
verifier.verifyLocation("p", False, 8)

print("..add 'i'")
value,offset = builder.get_next_value_and_offset()
result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("p", (8, 8))
verifier.set_state("pp", (9, -1))
verifier.verify()
verifier.verifyLocation("p", True, 8)

result = builder.process_value_at_location(value, offset)
assert(result == True)

verifier.set_state("pi", (10, -1))
verifier.verify()
verifier.verifyLocation(None, True, -1)

result = builder.process_value_at_location(value, offset)
assert(result == False)
verifier.verify()
verifier.verifyLocation("i", True, 1)

builder.finish()
printTree(root)

print("END TEST")
