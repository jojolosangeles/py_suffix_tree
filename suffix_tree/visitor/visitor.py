from queue import Queue
from suffix_tree.location import Location


class Visitor:
    def visit(self, node, nodeStore):
        pass

    def done(self):
        return False

    def after_children_visited(self, node):
        pass

class ComboVisitor:
    def __init__(self, *args):
        self.visitors = list(args)

    def visit(self, node, nodeStore):
        for v in self.visitors:
            v.visit(node, nodeStore)

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
            visitor.visit(node, None)
            if node.children != None:
                for child in node.children:
                    self.node_queue.put(node.children[child])

class NodeDFS:
    """Depth First Traversal.

    First visit the node, then visit each child of the node,
    let visitor know when all children for a given node have been visited."""
    def __call__(self, visitor, nodeStore, startNode):
        visitor.visit(startNode, nodeStore)
        if nodeStore.hasChildren(startNode.PK, startNode.SK):
            for child in nodeStore.children(startNode.PK):
                self(visitor, nodeStore, child)
                if visitor.done():
                    break
        visitor.after_children_visited(startNode)

class MergeSuffixTreeVisitor(Visitor):
    """Merge two suffix trees into one.

    Traverse the first suffix tree (ST1), for each node,
    - push the incoming edge start location
    - push the corresponding second suffix tree (ST2) location
    After visiting all children, pop those locations

    For each value on the incoming edge, match to second suffix tree.
    When a mismatch is encountered:
    - emit location of both trees
    - reset both tree location to most recent pushed location
    - continue ST1 traversal"""
    def __init__(self, st1, st2, mismatchLocations, traverser):
        self.st1 = st1
        self.st1location = Location()
        self.st1location.locateOnNode(st1.root)
        self.st2 = st2
        self.st2location = Location()
        self.st2location.locateOnNode(st2.root)
        self.mismatchLocations = mismatchLocations
        self.locationStack = []
        self.traverser = traverser
        self.doneForNow = False

    def visit(self, node, nodeStore):
        if node.hasIncomingEdgeValues():
            for value in node.iEVS:
                if not self.traverser.canFollowValue(self.st2location, value):
                    self.mismatchLocations.foundMismatch(self.st1location, self.st2location)
                    self.doneForNow = True

    def done(self):
        if self.doneForNow:
            self.doneForNow = False
            return True
        else:
            return False

class SuffixCollector(Visitor):
    """Collect the suffix offsets encountered by this visitor.

    This is done after traversing down the tree, ending at a node, to
    get all locations of the search sequence in the sequence of values."""
    def __init__(self):
        self.suffixes = []

    def visit(self, node, nodeStore):
        #print(f"node is {node}")
        if node.isLeafEdge:
            self.suffixes.append(node.sO)

class PrintVisitor:
    def __init__(self):
        self.visit_depth = 0

    def visit(self, node, nodeStore):
        self.visit_depth += 1
        if node.isRoot:
            print("root")
        else:
            print("{}lf={}, depth={}, {}-{}".format("   "*self.visit_depth, node.leaf_count, node.depth, node.incoming_edge_start_offset, "*" if node.incoming_edge_end_offset < 0 else node.incoming_edge_end_offset))

    def after_children_visited(self, node):
        self.visit_depth -= 1


class LeafCountVisitor:
    """Set the number of leaf nodes (leaf_count) at or below each node in the tree."""
    def visit(self, node, nodeStore):
        if node.isLeafEdge:
            node.leaf_count = 1

    def after_children_visited(self, node):
        if not node.isLeafEdge:
            node.leaf_count = sum([node.children[child].leaf_count for child in node.children])


class DepthVisitor(Visitor):
    """Set the depth of each node in the suffix tree."""
    def __init__(self, final_suffix_offset):
        self.final_suffix_offset = final_suffix_offset

    def visit(self, node, node_store):
        if node.isRoot:
            node.depth = 0
        elif node.isLeafEdge:
            node.depth = self.final_suffix_offset - node.iESO + node_store.getNode(node.PK).depth
        elif node.isInternalNode:
            node.depth = len(node.iEVS) + node_store.getNode(node.parentPK).depth

