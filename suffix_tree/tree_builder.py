from suffix_tree.node import TERMINAL_VALUE_OFFSET, TERMINAL_VALUE
from suffix_tree.node_store import NodeStore
from suffix_tree.node_factory import NodeFactory
from suffix_tree.traverser import Traverser
from suffix_tree.location import Location

PROCESSING_COMPLETE = False
VALUE_NEEDS_FURTHER_PROCESSING = True

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
                # 1 - insert below a node, by creating a LeafEdge child
                self.createLeafEdge(self.location.node.PK, value, offset)

                # if we are on the root, processing is complete
                if self.location.node.isRoot():
                    return PROCESSING_COMPLETE

                result = PROCESSING_COMPLETE if self.location.node.isRoot() else VALUE_NEEDS_FURTHER_PROCESSING
                self.debug_print(f"goToSuffix: {self.location}")
                self.traverser.goToSuffix(self.location)
                if self.location.on_node:
                    self.nodeFactory.suffixLinker.setLink(self.location.node)
                return VALUE_NEEDS_FURTHER_PROCESSING
            elif self.location.node.isLeafEdge():
                # 2 - insert on a LeafEdge at the location offset
                originalLeafEdge = self.location.node
                self.debug_print(f"originalLeafEdge: {originalLeafEdge}")
                iESO = originalLeafEdge.iESO
                internalNode = self.nodeFactory.createInternalNode(self.location.node.PK, self.dataSource[
                                                                                          iESO:iESO + self.location.incomingEdgeOffset])
                self.debug_print(f"internalNode: {internalNode}")
                internalEdge = self.nodeFactory.createInternalEdge(self.location.node.PK, self.location.node.SK,
                                                                   internalNode.PK)
                self.debug_print(f"internalEdge: {internalEdge}")
                self.nodeStore.registerNode(internalNode)
                self.nodeStore.registerNode(internalEdge)
                originalLeafEdge.iESO += self.location.incomingEdgeOffset
                originalLeafEdge.PK = internalNode.PK
                originalLeafEdge.SK = self.dataSource[originalLeafEdge.iESO]
                self.nodeStore.registerNode(originalLeafEdge)
                self.location.locateOnNode(internalNode)
                self.debug_print(f"modifiedLeafEdge: {originalLeafEdge}")
                self.debug_print(f"after inserting InternalEdge, InternalNode, modifying LeafEdge, expecting location on pass-through internal node")
                self.debug_print(self.location)
                self.debug_print(self.nodeStore)
                return VALUE_NEEDS_FURTHER_PROCESSING
            elif self.location.node.isInternalNode():
                original_iEVS = self.location.node.iEVS
                originalInternalNode = self.location.node
                internalNode = self.nodeFactory.createInternalNode(originalInternalNode.parentPK, original_iEVS[:self.location.incomingEdgeOffset])
                internalNodeParent = self.nodeStore.getNode(internalNode.parentPK)
                assert(internalNodeParent.isInternalNode())
                internalEdge = self.nodeFactory.createInternalEdge(internalNodeParent.PK, internalNode.iEVS[0], internalNode.PK)
                previousInternalEdge = self.nodeStore.getEdge(internalNode.parentPK, internalNode.iEVS[0])
                previousInternalEdge.PK = internalNode.PK
                previousInternalEdge.SK = original_iEVS[self.location.incomingEdgeOffset]
                originalInternalNode.iEVS = original_iEVS[self.location.incomingEdgeOffset:]
                originalInternalNode.parentPK = internalNode.PK

                self.nodeStore.registerNode(internalNode)
                self.nodeStore.registerNode(internalEdge)
                self.nodeStore.registerNode(previousInternalEdge)
                self.nodeStore.registerNode(originalInternalNode)
                self.location.locateOnNode(internalNode)
                self.debug_print(f"after inserting InternalEdge, InternalNode, modifying InternalEdge, expecting location on pass-through internal node")
                self.debug_print(self.location)
                self.debug_print(self.nodeStore)
                return VALUE_NEEDS_FURTHER_PROCESSING
            else:  # problem here
                raise(ValueError(f"Unclear what location node type is: {self.location.node}"))



    def createLeafEdge(self, PK, value, offset):
        leafEdge = self.nodeFactory.createLeafEdge(PK, value, offset)
        self.nodeStore.registerNode(leafEdge)