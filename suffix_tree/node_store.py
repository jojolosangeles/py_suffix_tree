from suffix_tree.node import SELF

class NodeStore:
    def __init__(self):
        self.store = {}

    def registerNode(self, node):
        if not node.PK in self.store:
            self.store[node.PK] = {}
        self.store[node.PK][node.SK] = node

    def hasChildren(self, PK, SK):
        return False if SK != SELF else PK in self.store and len(self.store[PK]) > 1

    def children(self, PK):
        partition = self.store[PK]
        edges = [ partition[key] for key in partition if key != SELF ]
        internalEdges = [ ie for ie in edges if ie.isInternalEdge() ]
        leafEdges = [ le for le in edges if le.isLeafEdge() ]
        internalNodes = [ self.getNode(ie.tN) for ie in internalEdges ]
        return internalNodes + leafEdges

    def getNode(self, PK):
        return self.store[PK][SELF]

    def getEdge(self, PK, SK):
        if PK not in self.store:
            print("yo 1")
        else:
            skg = self.store[PK]
            if SK not in skg:
                print("yo 2")
        return self.store[PK][SK]

    def hasEdge(self, PK, SK):
        return SK in self.store[PK]

    def __repr__(self):
        result = []
        result.append(f"{len(self.store)} nodes")
        for key in self.store:
            nodeInfo = self.store[key]
            result.append(f" {key}: {len(nodeInfo)} children")
            for child in nodeInfo:
                result.append(f"  {child} => {nodeInfo[child]}")
        return "\n".join(result)