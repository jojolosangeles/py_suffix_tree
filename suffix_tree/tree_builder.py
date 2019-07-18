from suffix_tree.node_store import NodeStore
from suffix_tree.node_factory import NodeFactory
from suffix_tree.traverser import Traverser
from suffix_tree.location import Location

class TreeBuilder:
    def __init__(self, dataSource):
        self.nodeStore = NodeStore()
        self.dataSource = dataSource + "!"
        self.traverser = Traverser(self.nodeStore, self.dataSource)
        self.nodeFactory = NodeFactory()
        self.root = self.nodeFactory.createRoot()
        self.nodeStore.registerNode(self.root)
        self.location = Location()
        self.location.locateOnNode(self.root)

    def process_all(self):
        count = 0
        for value in self.dataSource[:-1]:
            print(f"{count}: {value}")
            while self.processValue(value, count):
                print(self.location)
                print(self.nodeStore)
                input()
            print("--------")
            print(f"{self.location}")
            print(f"{self.nodeStore}")
            count += 1
            input()

    def process_all_values(self):
        count = 0
        for value in self.dataSource[:-1]:
            while self.processValue(value, count):
                pass
            count += 1
        terminal_value = -1
        while self.processValue(terminal_value, count):
            pass
        self.last_offset = count

    def processValue(self, value, offset):
        """process value and return True if there is more to do"""
        if self.traverser.canFollowValue(self.location, value):
            self.traverser.followValue(self.location, value)
            return False
        elif self.location.on_node:
            self.createLeafEdge(self.location.node.PK, value, offset)
            result = not self.location.node.isRoot()
            print(f"goToSuffix for {self.location}")
            self.traverser.goToSuffix(self.location)
            if self.location.on_node:
                self.nodeFactory.suffixLinker.setLink(self.location.node)
            return result
        elif self.location.node.isInternalNode():
            internalNode = self.nodeFactory.createInternalNode(self.location.node.PK, self.location.node.iEVS[:self.location.incomingEdgeOffset])
            internalNodeParent = self.nodeStore.getNode(internalNode.parentPK)
            assert(internalNodeParent.isInternalNode())
            internalEdge = self.nodeFactory.createInternalEdge(self.location.node.PK, internalNode.iEVS[0], internalNode.PK)
            self.nodeStore.registerNode(internalNode)
            self.nodeStore.registerNode(internalEdge)
            self.location.locateOnNode(internalNode)
            return True
        else:  # on a LeafEdge
            originalLeafEdge = self.location.node
            print(f"originalLeafEdge: {originalLeafEdge}")
            iESO = originalLeafEdge.iESO
            internalNode = self.nodeFactory.createInternalNode(self.location.node.PK, self.dataSource[iESO:iESO + self.location.incomingEdgeOffset])
            print(f"internalNode: {internalNode}")
            internalEdge = self.nodeFactory.createInternalEdge(self.location.node.PK, self.location.node.SK, internalNode.PK)
            print(f"internalEdge: {internalEdge}")
            self.nodeStore.registerNode(internalNode)
            self.nodeStore.registerNode(internalEdge)
            originalLeafEdge.iESO += self.location.incomingEdgeOffset
            originalLeafEdge.PK = internalNode.PK
            originalLeafEdge.SK = self.dataSource[originalLeafEdge.iESO]
            self.nodeStore.registerNode(originalLeafEdge)
            self.location.locateOnNode(internalNode)
            print(f"modifiedLeafEdge: {originalLeafEdge}")
            return True


    def createLeafEdge(self, PK, value, offset):
        leafEdge = self.nodeFactory.createLeafEdge(PK, value, offset)
        self.nodeStore.registerNode(leafEdge)