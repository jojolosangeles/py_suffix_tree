
class EdgeSplitter:
    def __init__(self, dataSource, nodeFactory, nodeStore):
        self.dataSource = dataSource
        self.nodeFactory = nodeFactory
        self.nodeStore = nodeStore

    def addLeafEdge(self, location, value, offset):
        self.nodeStore.registerNode(self.nodeFactory.createLeafEdge(location.node.PK, value, offset))

    def createInternalNode(self, parentPK, incomingString):
        parentSK = incomingString[0]
        internalNode = self.nodeFactory.createInternalNode(parentPK, incomingString)
        internalEdge = self.nodeFactory.createInternalEdge(parentPK, parentSK, internalNode.PK)
        self.nodeStore.newPK(internalNode.PK)
        self.nodeStore.registerNode(internalNode)
        self.nodeStore.registerNode(internalEdge)
        return internalNode

    def splitLeafEdge(self, location):
        originalLeafEdge = location.node
        iESO = originalLeafEdge.iESO
        internalEdgeString = self.dataSource[iESO:iESO + location.incomingEdgeOffset]
        internalNode = self.createInternalNode(originalLeafEdge.PK, internalEdgeString)
        originalLeafEdge.iESO += location.incomingEdgeOffset
        originalLeafEdge.PK = internalNode.PK
        originalLeafEdge.SK = self.dataSource[originalLeafEdge.iESO]
        self.nodeStore.registerNode(originalLeafEdge)
        location.locateOnNode(internalNode)
    
    def splitInternalEdge(self, location):
        """Split an edge at a given Location.  An Internal Node is inserted, and the Location is set to that node."""
        original_iEVS = location.node.iEVS
        originalInternalNode = location.node
        originalInternalEdge = self.nodeStore.getEdge(originalInternalNode.parentPK, original_iEVS[0])
        internalEdgeString = location.node.iEVS[:location.incomingEdgeOffset]
        internalNode = self.createInternalNode(originalInternalEdge.PK, internalEdgeString)
        originalInternalEdge.PK = internalNode.PK
        originalInternalEdge.SK = original_iEVS[location.incomingEdgeOffset]
        originalInternalNode.iEVS = original_iEVS[location.incomingEdgeOffset:]
        originalInternalNode.parentPK = internalNode.PK

        self.nodeStore.registerNode(originalInternalEdge)
        self.nodeStore.registerNode(originalInternalNode)
        location.locateOnNode(internalNode)
