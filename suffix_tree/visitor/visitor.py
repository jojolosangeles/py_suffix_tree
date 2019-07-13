from queue import Queue

from suffix_tree.node import Node

class Visitor:
    def visit(self, node):
        pass

    def after_children_visited(self, node):
        pass

class ComboVisitor:
    def __init__(self, *args):
        self.visitors = list(args)

    def visit(self, node):
        for v in self.visitors:
            v.visit(node)

    def after_children_visited(self, node):
        for v in self.visitors:
            v.after_children_visited(node)

class NodeBFS:
    """Visit each node in a tree with breadth-first traversal."""
    def __init__(self):
        self.node_queue = Queue()

    def __call__(self, visitor, node):
        """Traverse the tree with a visitor starting at a given node."""
        self.node_queue.put(node)
        self.bfs(visitor, node)

    def bfs(self, visitor, node):
        while not self.node_queue.empty():
            node = self.node_queue.get()
            visitor.visit(node)
            if node.children != None:
                for child in node.children:
                    self.node_queue.put(node.children[child])


class NodeDFS:
    def __call__(self, visitor, node):
        visitor.visit(node)
        if node.children != None:
            for child in node.children:
                self(visitor, node.children[child])
        visitor.after_children_visited(node)





class SuffixCollector(Visitor):
    """Collect the suffix offsets encountered by this visitor.

    This is done after traversing down the tree, ending at a node, to
    get all locations of the search sequence in the sequence of values."""
    def __init__(self, result):
        self.suffixes = result

    def visit(self, node):
        if node.is_leaf():
            self.suffixes.append(node.suffix_offset)

class PrintVisitor:
    def __init__(self):
        self.visit_depth = 0

    def visit(self, node):
        self.visit_depth += 1
        if node.is_root():
            print("root")
        else:
            print("{}lf={}, depth={}, {}-{}".format("   "*self.visit_depth, node.leaf_count, node.depth, node.incoming_edge_start_offset, "*" if node.incoming_edge_end_offset < 0 else node.incoming_edge_end_offset))

    def after_children_visited(self, node):
        self.visit_depth -= 1


class LeafCountVisitor:
    """Set the number of leaf nodes (leaf_count) at or below each node in the tree."""
    def visit(self, node):
        if node.is_leaf():
            node.leaf_count = 1

    def after_children_visited(self, node):
        if not node.is_leaf():
            node.leaf_count = sum([node.children[child].leaf_count for child in node.children])


class DepthVisitor(Visitor):
    """Set the depth of each node in the suffix tree."""
    def __init__(self, final_suffix_offset):
        self.final_suffix_offset = final_suffix_offset

    def visit(self, node):
        if node.is_root():
            node.depth = 0
        elif node.is_leaf():
            node.depth = self.final_suffix_offset - node.incoming_edge_start_offset + node.parent.depth
        else:
            node.depth = node.incoming_edge_length() + node.parent.depth


class OffsetAdjustingVisitor(Visitor):
    def __init__(self, starting_offset):
        self.starting_offset = starting_offset

    def visit(self, node):
        if node.incoming_edge_start_offset != Node.UNDEFINED_OFFSET:
            node.incoming_edge_start_offset += self.starting_offset
        if node.incoming_edge_end_offset != Node.UNDEFINED_OFFSET:
            node.incoming_edge_end_offset += self.starting_offset
