class Location:
    def __init__(self):
        self.on_node = False
        self.node = None
        self.incomingEdgeOffset = 0

    def locateOnNode(self, node):
        self.on_node = True
        self.node = node

    def locateOnEdge(self, edge, offset):
        self.on_node = False
        self.node = edge
        self.incomingEdgeOffset = offset

    def __repr__(self):
        if self.on_node:
            return f"On Node: {self.node}"
        elif self.node.isLeafEdge():
            return f"On LeafEdge: {self.node}, offset {self.incomingEdgeOffset}"
        else:
            return f"On Internal Node: {self.node}, offset {self.incomingEdgeOffset}"

