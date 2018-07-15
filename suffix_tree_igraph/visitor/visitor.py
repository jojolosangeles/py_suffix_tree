class Visitor:
    def visit(self, node_id):
        pass

    def after_children_visited(self, node_id):
        pass

class NodeDFS:
    def __init__(self, graph):
        self.graph = graph

    def __call__(self, visitor, node_id, final_id=0):
        visitor.visit(node_id, final_id)
        edges = self.graph.es.select(_from=node_id, suffix_link=False)
        for edge in edges:
            child_id = edge.tuple[1]
            self(visitor, child_id, final_id)
        visitor.after_children_visited(node_id)


class SuffixCollector(Visitor):
    def __init__(self, tree_graph):
        self.suffixes = []
        self.tree_graph = tree_graph

    def visit(self, node_id, final_id=0):
        if self.tree_graph.is_leaf(node_id):
            self.suffixes.append(self.tree_graph.get_suffix_offset(node_id))

