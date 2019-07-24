from suffix_tree.node import TERMINAL_VALUE_OFFSET, TERMINAL_VALUE
from suffix_tree.node_store import NodeStore
from suffix_tree.node_factory import NodeFactory
from suffix_tree.traverser import Traverser
from suffix_tree.location import Location
from suffix_tree.edge_splitter import EdgeSplitter

PROCESSING_COMPLETE = False
VALUE_NEEDS_FURTHER_PROCESSING = True

class TreeBuilder:
    def __init__(self, dataSource):
        self.nodeStore = NodeStore()
        self.dataSource = dataSource + "!"
        self.traverser = Traverser(self.nodeStore, self.dataSource)
        self.nodeFactory = NodeFactory()
        self.edgeSplitter = EdgeSplitter(dataSource, self.nodeFactory, self.nodeStore)
        self.root = self.nodeFactory.createRoot()
        self.nodeStore.newPK(self.root.PK)
        self.nodeStore.registerNode(self.root)
        self.location = Location()
        self.location.locateOnNode(self.root)
        self.debugOn = False

    def debug_print(self, s):
        if self.debugOn:
            print(s)

    def process_all(self):
        count = 0
        for value in self.dataSource[:TERMINAL_VALUE_OFFSET]:
            self.debug_print(f"{count}: {value}")
            while self.processValue(value, count) == VALUE_NEEDS_FURTHER_PROCESSING:
                self.debug_print(self.location)
                self.debug_print(self.nodeStore)
                input()
            self.debug_print("--------")
            self.debug_print(f"{self.location}")
            self.debug_print(f"{self.nodeStore}")
            count += 1
            input()

    def process_all_values(self):
        count = 0
        for value in self.dataSource[:TERMINAL_VALUE_OFFSET]:
            while self.processValue(value, count) == VALUE_NEEDS_FURTHER_PROCESSING:
                pass
            count += 1
        while self.processValue(TERMINAL_VALUE, count):
            pass
        self.last_offset = count
        #print("Node store:", self.nodeStore)

    def processValue(self, value, offset):
        """process value and return True if there is more to do"""
        if self.traverser.canFollowValue(self.location, value):
            self.traverser.followValue(self.location, value)
            return PROCESSING_COMPLETE
        else:
            # when we can't process the value, it has to be inserted
            # The three types of graph changes:
            # 1 - insert below a node, by creating a LeafEdge child
            # 2 - insert on a LeafEdge at the location offset
            # 3 - insert on an InternalEdge at the location offset
            if self.location.on_node:
                # Case No. 1 - insert a Leaf Edge child below the current Internal Node
                self.edgeSplitter.addLeafEdge(self.location, value, offset)
                if self.location.node.isRoot:
                    return PROCESSING_COMPLETE
                else:
                    self.traverser.goToSuffix(self.location)
                    if self.location.on_node:
                        self.nodeFactory.suffixLinker.setLink(self.location.node)
                    return VALUE_NEEDS_FURTHER_PROCESSING
            elif self.location.node.isLeafEdge:
                # Case No. 2 - insert an Internal Node on a LeafEdge at the location offset
                self.edgeSplitter.splitLeafEdge(self.location)
                return VALUE_NEEDS_FURTHER_PROCESSING
            elif self.location.node.isInternalNode:
                # Case No. 3 - insert an Internal Node on an Internal Edge at the location offset
                self.edgeSplitter.splitInternalEdge(self.location)
                return VALUE_NEEDS_FURTHER_PROCESSING
            else:  # problem here
                raise(ValueError(f"Unclear what location node type is: {self.location.node}"))



