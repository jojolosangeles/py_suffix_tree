from suffix_tree.location import Location
from suffix_tree.traverser import Traverser
from suffix_tree.visitor.visitor import NodeDFS, SuffixCollector

import re

class SuffixTree:
    def __init__(self, root, node_store, data_store):
        self.root = root
        self.node_store = node_store
        self.data_store = data_store

    def find_in_str(self, target_str, remaining_str):
        """Return a list of locations where the target_str is found in a string."""
        return [m.start() for m in re.finditer(target_str, remaining_str)]

    def find(self, target_str):
        """Returns a list of locations where the target_str is found in the sequence used to create the suffix tree."""
        location,found_entire_target = self.locate(target_str)
        if not found_entire_target:
            return []
        else:
            suffix_collector = SuffixCollector()
            nodeDFS = NodeDFS()
            nodeDFS(suffix_collector, self.node_store, location.node)
            return suffix_collector.suffixes

    def locate(self, target_str):
        """Returns the Location of the target_str in the SuffixTree, and True if the entire target_str is found"""
        location = Location()
        location.locateOnNode(self.root)
        traverser = Traverser(self.node_store, self.data_store)
        for value in target_str:
            if not traverser.canFollowValue(location, value):
                return location, False
            traverser.followValue(location, value)
        return location, True

    def apply(self, visitor):
        nodeDFS = NodeDFS()
        nodeDFS(visitor, self.node_store, self.root)
