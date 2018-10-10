from suffix_tree.node import RootNode, LeafNode, Node
from itertools import count


class NodeFactory:
    """NodeFactory is used by the Ukkonen algorithm implementation to create Node instances
    as a sequence of values is processed."""
    def __init__(self, suffix_linker):
        self.suffix_generator = (i for i in count())
        self.id_generator = (i for i in count())
        self.suffix_linker = suffix_linker

    def final_id(self):
        return next(self.id_generator)

    def final_suffix(self):
        return next(self.suffix_generator)

    def create_leaf(self, node, value, offset):
        leaf = LeafNode(next(self.id_generator), offset, next(self.suffix_generator))
        self.add_child(node, value, leaf)
        return leaf

    def create_internal(self, incoming_edge_start_value, node, value_at_split_offset, edge_split_offset):
        """Internal nodes are created by splitting the incoming edge to a node, placing a new
        node on that edge.

        Start State:
           incoming_edge_start_offset                                         incoming_edge_end_offset
                a, a+1, a+2, ... a+edge_split_offset, a+edge_split_offset+1, ... a+N

        End State:
           ORIGINAL Node parent:
             children:
                 key: incoming_edge_start_value
                 value: NEW Node

           NEW Node: takes part of original Nodes incoming edge, ORIGINAL parent refers to this node,
             incoming_edge_start_offset   incoming_edge_end_offset
                   a, a+1, ...              a+edge_split_offset
             children (only one):
                 key: value_at_split_offset
                 value: ORIGINAL Node

           ORIGINAL Node: NEW Node is the parent,
             incoming_edge_start_offset      incominge_edge_end_offset
                  a+edge_split_offset+1, ....  a+N
        """
        new_node = Node(next(self.id_generator), node.incoming_edge_start_offset, edge_split_offset, {value_at_split_offset: node}, None)
        node.incoming_edge_start_offset = edge_split_offset + 1
        self.add_child(node.parent, incoming_edge_start_value, new_node)
        node.parent = new_node
        self.suffix_linker.needs_suffix_link(new_node)
        return new_node

    def create_root(self):
        return RootNode(next(self.id_generator))

    def add_child(self, parent, value, child):
        parent.children[value] = child
        child.parent = parent

