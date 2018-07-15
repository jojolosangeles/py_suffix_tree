from igraph import Graph
from itertools import count

from suffix_tree_igraph.suffix_linker import SuffixLinker


class IgraphStrategy:
    def __init__(self):
        self.g = Graph(directed=True)

    # creational: create_root, create_leaf, create_node, split_edge, remove_edge
    def create_root(self):
        return self.create_node()

    def create_leaf(self, suffix_offset, parent, value, offset):
        leaf = self.create_node()
        self.g.vs[leaf]['suffix_offset'] = suffix_offset
        self.add_child_link(parent, leaf, value, offset, -1)
        return leaf

    def create_node(self):
        self.g.add_vertices(1)
        return len(self.g.vs) - 1

    def split_edge(self,
                   parent, parent_key, new_node_start_offset, new_node_end_offset,
                   child, new_node_child_key, new_child_start_offset, new_child_end_offset):
        new_node = self.create_node()
        self.add_child_link(parent, new_node, parent_key, new_node_start_offset, new_node_end_offset)
        self.add_child_link(new_node, child, new_node_child_key, new_child_start_offset, new_child_end_offset)
        self.remove_child_link(parent, child)
        return new_node

    # linking: add_suffix_link, add_child_link
    def add_suffix_link(self, v1, v2):
        self.g.add_edge(v1, v2, suffix_link=True)

    def get_suffix_link(self, v):
        edges = self.g.es.select(_from=v, suffix_link=True)
        if len(edges) == 1:
            return edges[0].tuple[1], edges[0]['so'], edges[0]['eo']
        return None, None, None

    def add_child_link(self, v1, v2, value, incoming_edge_start_offset, incoming_edge_end_offset):
        self.g.add_edge(v1, v2, suffix_link=False, key=value, so=incoming_edge_start_offset, eo=incoming_edge_end_offset)

    def remove_child_link(self, v1, v2):
        self.g.delete_edges([(v1, v2)])

    # informational: get_parent, get_incoming_edge
    def get_parent(self, v):
        edge = self.get_incoming_edge(v)
        return edge.tuple[0]

    def get_incoming_edge(self, v):
        edges = self.g.es.select(_to=v, suffix_link=False)
        if len(edges) == 1:
            edge = edges[0]
            return edge
        raise ValueError

    def get_incoming_edge_offsets(self, v):
        edge = self.get_incoming_edge(v)
        return edge['so'], edge['eo']

    def has_outgoing_edge(self, v, value):
        try:
            edges = self.g.es.select(_from=v, key=value, suffix_link=False)
            if len(edges) == 1:
                return True, edges[0].tuple[1], edges[0]['so'], edges[0]['eo']
        except KeyError:
            pass # when no edges exist in entire graph
        return False, None, None, None

    def get_suffix_offset(self, leaf):
        return self.g.vs[leaf]['suffix_offset']


class SuffixTreeGraph:
    def __init__(self, strategy):
        self.strategy = strategy
        self.root = self.strategy.create_root()
        self.strategy.add_suffix_link(self.root, self.root)
        self.suffix_generator = (i for i in count())
        self.suffix_linker = SuffixLinker(self.strategy.add_suffix_link)

    def is_root(self, node):
        return node == self.root

    def is_leaf(self, node):
        so, eo = self.get_incoming_edge_offsets(node)
        return so > eo

    def get_parent(self, node):
        return self.strategy.get_parent(node)

    def get_incoming_edge_offsets(self, node):
        return self.strategy.get_incoming_edge_offsets(node)

    def get_suffix_link(self, node):
        return self.strategy.get_suffix_link(node)

    def get_suffix_offset(self, leaf):
        return self.strategy.get_suffix_offset(leaf)

    def has_outgoing_edge(self, node, key):
        return self.strategy.has_outgoing_edge(node, key)

    def create_leaf(self, parent, value, offset):
        return self.strategy.create_leaf(next(self.suffix_generator), parent, value, offset)

    def create_internal(self, parent_key, node, new_node_child_key, new_node_end_offset):
        incoming_edge_start_offset, incoming_edge_end_offset = self.strategy.get_incoming_edge_offsets(node)
        parent = self.strategy.get_parent(node)
        new_node = self.strategy.split_edge(
            parent, parent_key, incoming_edge_start_offset, new_node_end_offset,
            node, new_node_child_key, new_node_end_offset + 1, incoming_edge_end_offset)
        self.suffix_linker.needs_suffix_link(new_node)
        return new_node