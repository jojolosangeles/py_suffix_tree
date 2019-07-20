from itertools import count
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.node import ROOT, SELF, Node

class NodeFactory:
    def __init__(self):
        self.internalIdGenerator = (i for i in count(1))
        self.suffixGenerator = (i for i in count())
        self.suffixLinker = SuffixLinker()

    def createRoot(self):
        result = Node(ROOT, SELF)
        result.sL = ROOT
        result.iEVS = ""
        return result

    def createInternalNode(self, parentPK, iEVS):
        result = Node(next(self.internalIdGenerator), SELF)
        result.iEVS = iEVS
        result.parentPK = parentPK
        self.suffixLinker.nodeNeedsSuffixLink(result)
        return result

    def createLeafEdge(self, PK, value, dsOffset):
        result = Node(PK, value)
        result.iESO = dsOffset
        result.sO = next(self.suffixGenerator)
        return result

    def createInternalEdge(self, parentPK, SK, targetPK):
        result = Node(parentPK, SK)
        result.tN = targetPK
        return result



