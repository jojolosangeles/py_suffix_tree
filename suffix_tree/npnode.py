ROOT = 0
SELF = 0

# attributes with values dependent on node type
SUFFIX_OFFSET = "sO"                    # LeafEdge
INTERNAL_EDGE_START_OFFSET = "iESO"     # LeafEdge
INTERNAL_EDGE_VALUE_SEQUENCE = "iEVS"   # Root, InternalNode
SUFFIX_OFFSET = "sO"                    # LeafEdge
SUFFIX_LINK = "sL"                      # Root, InternalNode
TARGET_NODE = "tN"                      # Internal Edge
SK = "SK"
PK = "PK"
PARENT_LINK = "pL"

IS_LEAF_EDGE = "isLeafEdge"
IS_INTERNAL_EDGE = "isInternalEdge"
IS_INTERNAL_NODE = "isInternalNode"
IS_ROOT = "isRoot"
HAS_SUFFIX_LINK = "hasSuffixLink"

NO_NODE = -1
NO_OFFSET = -1
NO_VALUE_SEQUENCE = ""
TERMINAL_VALUE = -1
TERMINAL_VALUE_OFFSET = -1

class NpNode:
    count = 0
    def __init__(self, PK, SK):
        self.PK = PK
        self.SK = SK

        self.NpNodeID = NpNode.count
        NpNode.count += 1

        self.isLeafEdge = False
        self.isInternalEdge = False
        self.isInternalNode = False
        self.isRoot = False
        self.hasSuffixLink = False

        # guarantee value for all fields
        self.sO = NO_OFFSET
        self.iESO = NO_OFFSET
        self.iEVS = NO_VALUE_SEQUENCE
        self.sL = NO_NODE
        self.tN = NO_NODE
        self.pL = NO_NODE

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