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
        return [m.start() for m in re.finditer(target_str, remaining_str)]

    def find(self, target_str):
        location = Location()
        location.locateOnNode(self.root)
        traverser = Traverser(self.node_store, self.data_store)
        suffix_collector = SuffixCollector()
        for value in target_str:
            if not traverser.canFollowValue(location, value):
                return []
            traverser.followValue(location, value)

        nodeDFS = NodeDFS()
        nodeDFS(suffix_collector, self.node_store, location.node)
        return suffix_collector.suffixes


