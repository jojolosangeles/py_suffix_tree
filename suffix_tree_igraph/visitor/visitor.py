from suffix_tree_igraph.igraph_adapter import ig_print, igraph_suffix_offset, igraph_is_leaf


class Visitor:
    def visit(self, node_id):
        pass

    def after_children_visited(self, node_id):
        pass

class NodeDFS:
    def __init__(self, graph, node_factory):
        self.graph = graph
        self.node_factory = node_factory

    def __call__(self, visitor, node_id, final_id=0):
        visitor.visit(node_id, final_id)
        edges = self.graph.es.select(_from=node_id, suffix_link=False)
        for edge in edges:
            child_id = edge.tuple[1]
            self(visitor, child_id, final_id)
        visitor.after_children_visited(node_id)


class SuffixCollector(Visitor):
    def __init__(self):
        self.suffixes = []

    def visit(self, node_id, final_id=0):
        if igraph_is_leaf(node_id):
            self.suffixes.append(igraph_suffix_offset(node_id))

class PrintVisitor:
    def __init__(self):
        self.visit_depth = 0

    def visit(self, node, final_id):
        self.visit_depth += 1
        if node.is_root():
            ig_print("root")
        else:
            ig_print("{}lf={}, depth={}, {}-{}".format("   "*self.visit_depth, node.leaf_count, node.depth, node.incoming_edge_start_offset, "*" if node.incoming_edge_end_offset < 0 else node.incoming_edge_end_offset))

    def after_children_visited(self, node):
        self.visit_depth -= 1

class LeafCountVisitor:
    def __init__(self, final_id):
        self.final_id = final_id

    def visit(self, node_id, final_id):
        if igraph_is_leaf(node_id):
            #node.leaf_count = 1
            pass

    def after_children_visited(self, node):
        if not node.is_leaf():
            #node.leaf_count = sum([node.children[child].leaf_count for child in node.children])
            pass

class DepthVisitor(Visitor):
    def visit(self, node, final_id):
        if node.is_root():
            node.depth = 0
        elif node.is_leaf():
            node.depth = final_id - node.incoming_edge_start_offset + node.parent.depth
        else:
            node.depth = node.incoming_edge_length() + node.parent.depth
