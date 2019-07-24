from suffix_tree.node import SELF

"""
Using the PK, SK style of DynamoDb, what is the appropriate Numpy or Pandas representation?
What I am looking for is ability to just use a Pandas DataFrame as an in-memory database.

For example, the Suffix Tree graph representation uses PK, SK as an index.
This corresponds to a Pandas MultiIndex"""
class NodeStore:
    """The NodeStore contains all Nodes in the suffix tree."""
    def __init__(self):
        self.store = {}

    def newPK(self, PK):
        self.store[PK] = {}

    def registerNode(self, node):
        # if not node.PK in self.store:
        #     self.store[node.PK] = {}
        self.store[node.PK][node.SK] = node

    def hasChildren(self, PK, SK):
        return False if SK != SELF else PK in self.store and len(self.store[PK]) > 1

    def children(self, PK):
        partition = self.store[PK]
        edges = [ partition[key] for key in partition if key != SELF ]
        internalEdges = [ ie for ie in edges if ie.isInternalEdge ]
        leafEdges = [ le for le in edges if le.isLeafEdge ]
        internalNodes = [ self.getNode(ie.tN) for ie in internalEdges ]
        return internalNodes + leafEdges

    def getNode(self, PK):
        """Nodes are between edges.
        The Root Node has itself as it's parent and it's suffix link.  PK=ROOT, SK=SELF
        An Internal Node has a parent, and at least one child.  PK=ID, SK=SELF
        A Leaf Edge has a parent Node, an incoming edge start offset, and a suffix offset.  PK=(parent PK), SK=value"""
        return self.store[PK][SELF]

    def getEdge(self, PK, SK):
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

class NodeStorePersist:
    def __init__(self, filePath):
        self.filePath = filePath

    def persist(self, nodeStore):
        with open(self.filePath, "w") as outputFile:
            for key in nodeStore.store:
                nodeInfo = nodeStore.store[key]
                # print(f" {key}: {len(nodeInfo)} children")
                for child in nodeInfo:
                    node = nodeInfo[child]
                    outputFile.write(
                        f"{node.PK}|{node.SK}|{node.sO}|{node.iEVS}|{node.sL}|{node.tN}|{node.isLeafEdge}|{node.isInternalEdge}|{node.isInternalNode}|{node.isRoot}|{node.hasSuffixLink}\n")

