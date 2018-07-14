from igraph import *


class IgraphAdapter:
    def __init__(self):
        self.g = Graph(directed=True)
        self.has_edges = False

    def add_vertices(self, n):
        self.g.add_vertices(n)

    def add_edge(self, parent_offset, child_offset, value_key, start_offset, end_offset):
        self.g.add_edge(parent_offset, child_offset, key=value_key, so=start_offset, eo=end_offset)
        self.has_edges = True

    def remove_edge(self, from_vertex_id, to_vertex_id):
        self.g.delete_edges([(from_vertex_id, to_vertex_id)])

    def has_outgoing_edge(self, id, value):
        if self.has_edges:
            edges = self.g.es.select(_from=id, key=value)
            if len(edges) == 1:
                return True, edges[0].tuple[1]
        return None, False


ig_adapter = IgraphAdapter()


def no_print(*args, **kwargs):
    pass


ig_print = no_print

def igraph_reset():
    global ig_adapter
    ig_adapter = IgraphAdapter()


def igraph_add_vertex():
    ig_adapter.add_vertices(1)


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
