from suffix_tree.node import Node


class Visitor:
    def visit(self, node):
        pass

    def after_children_visited(self, node):
        pass

class NodeDFS:
    def __call__(self, visitor, node, final_id=0):
        visitor.visit(node, final_id)
        if not node.is_leaf():
            for key in node.children_ids:
                self(visitor, Node.get(node.children_ids[key]), final_id)
        visitor.after_children_visited(node)

class SuffixCollector(Visitor):
    def __init__(self):
        self.suffixes = []

    def visit(self, node, final_id=0):
        assert(node.is_leaf() == Node.is_leaf_id(node.id))
        if node.is_leaf():
            self.suffixes.append(node.suffix_offset)

class PrintVisitor:
    def __init__(self):
        self.visit_depth = 0

    def visit(self, node, final_id):
        self.visit_depth += 1
        if node.is_root():
            print("root")
        else:
            print("{}lf={}, depth={}, {}-{}".format("   "*self.visit_depth, node.leaf_count, node.depth, node.incoming_edge_start_offset, "*" if node.incoming_edge_end_offset < 0 else node.incoming_edge_end_offset))

    def after_children_visited(self, node):
        self.visit_depth -= 1

class LeafCountVisitor:
    def __init__(self, final_id):
        self.final_id = final_id

    def visit(self, node, final_id):
        if node.is_leaf():
            node.leaf_count = 1

    def after_children_visited(self, node):
        if not node.is_leaf():
            node.leaf_count = sum([Node.get(node.children_ids[key]).leaf_count for key in node.children_ids])

class DepthVisitor(Visitor):
    def visit(self, node, final_id):
        if node.is_root():
            node.depth = 0
        elif node.is_leaf():
            node.depth = Node.incoming_edge_start_offset(node.id) + Node.parent(node.id).depth
        else:
            node.depth = Node.incoming_edge_length(node.id) + Node.parent(node.id).depth
