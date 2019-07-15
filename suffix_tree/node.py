"""Node within a suffix tree."""

ROOT = "ROOT"
LEAF = "LEAF"
INTERNAL = "INNR"
SELF = "self"

class GraphNode:
    """The GraphNode is the replacement for the Node, and modelled after dynamoDB table design.
╔══════════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╗
║  PK      ║  SK  ║ iESO ║ iEVS ║ tNID ║ pNID ║ sO   ║ sL   ║
╠══════════╬══════╬══════╬══════╬══════╬══════╬══════╬══════╣
║  root    ║ self ║  -   ║  -   ║  -   ║  -   ║  -   ║  -   ║
║  root    ║ A    ║  -   ║  -   ║  i1  ║  -   ║  -   ║  -   ║
║  root    ║ B    ║  -   ║  -   ║  i2  ║  -   ║  -   ║  -   ║
║  root    ║ X    ║  2   ║  -   ║  -   ║ root ║  2   ║  -   ║
║  root    ║ Y    ║  3   ║  -   ║  -   ║ root ║  3   ║  -   ║
║  root    ║ C    ║  6   ║  -   ║  -   ║ root ║  6   ║  -   ║
║  root    ║ D    ║  7   ║  -   ║  -   ║ root ║  7   ║  -   ║
╠══════════╬══════╬══════╬══════╬══════╬══════╬══════╬══════╣
║   i1     ║ self ║  -   ║ AB   ║  -   ║ root ║  -   ║  i2  ║
║   i1     ║ X    ║  2   ║  -   ║  -   ║ i1   ║  0   ║  -   ║
║   i1     ║ C    ║  6   ║  -   ║  -   ║ i1   ║  4   ║  -   ║
╠══════════╬══════╬══════╬══════╬══════╬══════╬══════╬══════╣
║   i2     ║ self ║  -   ║ B    ║  -   ║ root ║  -   ║  -   ║
║   i2     ║ X    ║  2   ║  -   ║  -   ║ i2   ║  1   ║  -   ║
║   i2     ║ C    ║  6   ║  -   ║  -   ║ i2   ║  5   ║  -   ║
╚══════════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╝

For refactoring, first I will have the GraphEntity hold the data for the node
    """

    def __init__(self, PK, SK):
        self.PK = PK
        self.SK = SK

    def is_root(self):
        return self.PK == ROOT and self.SK == SELF

    def is_leaf(self):
        return hasattr(self, 'suffixOffset')

    def hasChildren(self):
        return self.SK == SELF

    def incomingEdgeLength(self):
        return len(self.incomingEdgeValueSequence) if hasattr(self, 'incomingEdgeValueSequence') else None

    def __repr__(self):
        if self.is_leaf():
            node_type = LEAF
            result = f"{self.PK}/{self.SK} Leaf={self.suffixOffset}, iESO={self.iESO}"
        elif self.is_root():
            result = f"{self.PK}"
        else:
            if hasattr(self, 'suffixLink'):
                skpart = f" sL->{self.suffixLink.PK}"
            else:
                skpart = "(needs Suffix Link)"
            if hasattr(self, 'incomingEdgeValueSequence'):
                prefix = f"{self.PK} \"{self.incomingEdgeValueSequence}\""
            else:
                prefix = "\"??? UNEXPECTED!  MISSING incomingEdgeValueSequence ???\""
            result = f"{prefix} {skpart}"
        return result

    @staticmethod
    def create_root():
        root = GraphNode(PK=ROOT, SK=SELF)
        root.suffixLink = root
        return root

    @staticmethod
    def create_leaf(PK, value, incomingEdgeStartOffset, suffixOffset):
        leaf = GraphNode(PK=PK, SK=value)
        leaf.iESO = incomingEdgeStartOffset
        leaf.suffixOffset = suffixOffset
        return leaf

    @staticmethod
    def create_internal(PK, incomingEdgeValueSequence):
        internal = GraphNode(PK=PK, SK=SELF)
        internal.incomingEdgeValueSequence = incomingEdgeValueSequence
        return internal

