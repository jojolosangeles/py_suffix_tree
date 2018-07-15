from igraph import *


class IgraphAdapter:
    def __init__(self):
        self.g = Graph(directed=True)
        self.has_edges = False

    def instance(self):
        return self.g

    def suffix_offset(self, vertex_id):
        return self.g.vs[vertex_id]['suffix_offset']

    def get_incoming_edge_offsets(self, vertex_id):
        edge = self.get_incoming_edge(vertex_id)
        return edge['so'], edge['eo']

    def get_incoming_edge_start_offset(self, vertex_id):
        edge = self.get_incoming_edge(vertex_id)
        return edge['so']

    def get_incoming_edge_end_offset(self, vertex_id):
        edge = self.get_incoming_edge(vertex_id)
        return edge['eo']

    def add_leaf(self, suffix_offset):
        id = len(self.g.vs)
        self.add_vertices(1)
        self.g.vs[id]['suffix_offset'] = suffix_offset

    def add_vertices(self, n):
        self.g.add_vertices(n)

    def add_edge(self, parent_offset, child_offset, value_key, start_offset, end_offset):
        self.g.add_edge(parent_offset, child_offset, key=value_key, so=start_offset, eo=end_offset, suffix_link=False)
        self.has_edges = True

    def remove_edge(self, from_vertex_id, to_vertex_id):
        self.g.delete_edges([(from_vertex_id, to_vertex_id)])

    def parent_id(self, node_id):
        edges = self.g.es.select(_to=node_id, suffix_link=False)
        return edges[0].tuple[0]

    def get_suffix_link(self, node_id):
        edges = self.g.es.select(_from=node_id, suffix_link=True)
        if len(edges) == 1:
            return edges[0].tuple[1]
        return None

    def get_incoming_edge(self, vertex_id):
        edges = self.g.es.select(_to=vertex_id, suffix_link=False)
        if len(edges) == 1:
            edge = edges[0]
            return edge
        raise ValueError

    def get_incoming_edge_length(self, vertex_id):
        edge = self.get_incoming_edge(vertex_id)
        return edge['eo'] - edge['so'] + 1

    def is_leaf(self, vertex_id):
        return self.get_suffix_link(vertex_id) == None

    def is_root(self, vertex_id):
        return self.get_suffix_link(vertex_id) == vertex_id

    def add_suffix_link(self, from_id, to_id):
        self.g.add_edge(from_id, to_id, suffix_link=True)

    def has_outgoing_edge(self, id, value):
        if self.has_edges:
            edges = self.g.es.select(_from=id, key=value, suffix_link=False)
            if len(edges) == 1:
                return True, edges[0].tuple[1]
        return None, False


ig_adapter = IgraphAdapter()


def no_print(*args, **kwargs):
    pass


ig_print = no_print


def igraph_instance():
    return ig_adapter.instance()


def igraph_suffix_offset(id):
    return ig_adapter.suffix_offset(id)


def igraph_reset():
    global ig_adapter
    ig_adapter = IgraphAdapter()


def igraph_parent_id(node_id):
    return ig_adapter.parent_id(node_id)


def igraph_add_vertex():
    ig_adapter.add_vertices(1)


def igraph_add_leaf(suffix_offset):
    ig_adapter.add_leaf(suffix_offset)


def igraph_add_edge(from_id, to_id, edge_key, start_offset, end_offset):
    ig_print("igraph_add_edge {} to {}".format(from_id, to_id))
    ig_adapter.add_edge(from_id, to_id, edge_key, start_offset, end_offset)


def igraph_remove_edge(from_id, to_id):
    ig_print("igraph_remove_edge {} to {}".format(from_id, to_id))
    ig_adapter.remove_edge(from_id, to_id)


def igraph_print_tree(nodestr, root, location):
    ig_print(nodestr.tree_str(root))


def igraph_has_outgoing_edge(id, value):
    return ig_adapter.has_outgoing_edge(id, value)


def igraph_add_suffix_link(from_id, to_id):
    ig_adapter.add_suffix_link(from_id, to_id)


def igraph_get_suffix_link(from_id):
    return ig_adapter.get_suffix_link(from_id)


def igraph_get_incoming_edge_length(id):
    return ig_adapter.get_incoming_edge_length(id)


def igraph_get_incoming_edge_offsets(id):
    return ig_adapter.get_incoming_edge_offsets(id)


def igraph_get_incoming_edge_end_offset(id):
    if igraph_is_root(id):
        return -1
    return ig_adapter.get_incoming_edge_end_offset(id)


def igraph_get_incoming_edge_start_offset(id):
    if igraph_is_root(id):
        return -1
    return ig_adapter.get_incoming_edge_start_offset(id)


# about the vertex
def igraph_is_leaf(id):
    return ig_adapter.is_leaf(id)


def igraph_is_root(id):
    return ig_adapter.is_root(id)
