class Traverser:
    def __init__(self, nodeStore, dataSource):
        self.nodeStore = nodeStore
        self.dataSource = dataSource

    def canFollowValue(self, location, value):
        if location.on_node:
            return self.nodeStore.hasEdge(location.node.PK, value)
        elif location.node.isLeafEdge():
            return self.dataSource[location.node.iESO + location.incomingEdgeOffset] == value
        else:
            return location.node.iEVS[location.incomingEdgeOffset] == value

    def followValue(self, location, value):
        if location.on_node:
            edge = self.nodeStore.getEdge(location.node.PK, value)
            location.node = edge if edge.isLeafEdge() else self.nodeStore.getNode(edge.tN)
            location.on_node = location.node.isInternalNode() and len(location.node.iEVS) == 1
            location.incomingEdgeOffset = 0 if location.on_node else 1
        elif location.node.isInternalNode():
            location.incomingEdgeOffset += 1
            location.on_node = location.incomingEdgeOffset == len(location.node.iEVS)
        else:
            location.incomingEdgeOffset += 1

    def goToSuffix(self, location):
        # if we are on a node with suffix link, follow that link
        if location.on_node:
            if location.node.hasSuffixLink():
                location.locateOnNode(self.nodeStore.getNode(location.node.sL))
            else:
                downStr = location.node.iEVS
                parentNode = self.nodeStore.getNode(location.node.parentPK)
                if parentNode.isRoot():
                    downStr = downStr[1:]
                parentNode = self.nodeStore.getNode(parentNode.sL)
                location.locateOnNode(parentNode)
                self.skipJumpDown(location, downStr)
        else:
            if location.node.isLeafEdge():
                iESO = location.node.iESO
                downStr = self.dataSource[iESO:iESO + location.incomingEdgeOffset]
            else:
                downStr = location.node.iEVS[:location.incomingEdgeOffset]
            node = self.nodeStore.getNode(location.node.PK)
            if node.isRoot():
                downStr = downStr[1:]
            else:
                node = self.nodeStore.getNode(node.sL)
            location.locateOnNode(node)
            self.skipJumpDown(location, downStr)


    def skipJumpDown(self, location, downStr):
        if len(downStr) > 0:
            if location.on_node:
                edge = self.nodeStore.getEdge(location.node.PK, downStr[0])
                if edge.isLeafEdge():
                    location.locateOnEdge(edge, len(downStr))
                else:
                    internalNode = self.nodeStore.getNode(edge.tN)
                    if len(downStr) > len(internalNode.iEVS):
                        downStr = downStr[len(internalNode.iEVS):]
                        location.locateOnNode(internalNode)
                        self.skipJumpDown(location, downStr)
                    elif len(downStr) == len(internalNode.iEVS):
                        location.locateOnNode(internalNode)
                    else:
                        location.locateOnEdge(internalNode, len(downStr))
