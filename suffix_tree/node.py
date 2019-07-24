ROOT = 0
SELF = "SELF"

# attributes with values dependent on node type
SUFFIX_OFFSET = "sO"                    # LeafEdge
INTERNAL_EDGE_VALUE_SEQUENCE = "iEVS"   # Root, InternalNode
SUFFIX_LINK = "sL"                      # Root, InternalNode
TARGET_NODE = "tN"                      # Internal Edge

TERMINAL_VALUE = -1
TERMINAL_VALUE_OFFSET = -1
NO_NODE = -1

class Node:
    count = 0
    def __init__(self, PK, SK):
        self.PK = PK
        self.SK = SK
        self.sO = TERMINAL_VALUE_OFFSET
        self.iEVS = ""
        self.sL = NO_NODE
        self.tN = NO_NODE

        Node.count += 1
        self.isLeafEdge = False
        self.isInternalEdge = False
        self.isInternalNode = False
        self.isRoot = False
        self.hasSuffixLink = False

    def hasIncomingEdgeValues(self):
        return len(self.iEVS) > 0

    def __repr__(self):
        if self.isRoot:
            return "root"
        elif self.isInternalNode:
            sL = self.sL if self.hasSuffixLink else "(missing suffix link)"
            return f"node.{self.PK}, {self.SK} \"{self.iEVS}\" sL: {sL}"
        elif self.isLeafEdge:
            return f"{self.PK}.{self.SK} to LeafEdge.{self.sO}, iESO {self.iESO}"
        else:
            return f"edge.{self.PK}.{self.SK} to node.{self.tN}"