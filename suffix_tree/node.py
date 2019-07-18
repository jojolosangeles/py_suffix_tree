ROOT = "ROOT"
SELF = "SELF"

SUFFIX_OFFSET = "sO"
INTERNAL_EDGE_VALUE_SEQUENCE = "iEVS"
SUFFIX_LINK = "sL"
TARGET_NODE = "tN"

class Node:
    def __init__(self, PK, SK):
        self.PK = PK
        self.SK = SK

    def isLeafEdge(self):
        return hasattr(self, SUFFIX_OFFSET)

    def isInternalEdge(self):
        return hasattr(self, TARGET_NODE)

    def isInternalNode(self):
        return hasattr(self, INTERNAL_EDGE_VALUE_SEQUENCE)

    def isRoot(self):
        return self.PK == ROOT and self.SK == SELF

    def hasSuffixLink(self):
        return hasattr(self, SUFFIX_LINK)

    def __repr__(self):
        if self.isRoot():
            return "root"
        elif self.isInternalNode():
            sL = self.sL if self.hasSuffixLink() else "(missing suffix link)"
            return f"internal-{self.PK}, {self.SK} \"{self.iEVS}\" sL: {sL}"
        elif self.isLeafEdge():
            return f"{self.PK}, {self.SK}, sO {self.sO}, iESO {self.iESO}"
        else:
            return f"Internal Edge from {self.PK} on value {self.SK} to {self.tN}"