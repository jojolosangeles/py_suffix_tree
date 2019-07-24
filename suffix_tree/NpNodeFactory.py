import numpy as np
from itertools import count
from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.npnode import ROOT, SELF, NpNode

class NpNodeFactory:


    def __init__(self):
        self.internalIdGenerator = (i for i in count(1))
        self.suffixGenerator = (i for i in count())
        self.suffixLinker = SuffixLinker()
        nodeTemplate = NpNode(0,0)
        npDict = { NpNode.SK: nodeTemplate.SK,
                   NpNode.PK: nodeTemplate.PK,
                   NpNode.SUFFIX_OFFSET: nodeTemplate.sO,
                   NpNode.INTERNAL_EDGE_VALUE_SEQUENCE: nodeTemplate.iEVS,
                   NpNode.SUFFIX_LINK: nodeTemplate.sL,
                   NpNode.TARGET_NODE: nodeTemplate.tN,
                   NpNode.PARENT_LINK: nodeTemplate.pL,
                   NpNode.IS_LEAF_EDGE: nodeTemplate.isLeafEdge,
                   NpNode.IS_INTERNAL_EDGE: nodeTemplate.isInternalEdge,
                   NpNode.IS_INTERNAL_NODE: nodeTemplate.isInternalNode,
                   NpNode.IS_ROOT: nodeTemplate.isRoot,
                   NpNode.HAS_SUFFIX_LINK: nodeTemplate.hasSuffixLink
                   }
        self.list = [ npDict.copy() for _ in range(100000)]
        self.nodeData = np.Series(self.list)

    def createRoot(self):
        result = self.nodeData[NpNode.ROOT]
        result[NpNode.SUFFIX_LINK] = ROOT
        result[NpNode.INTERNAL_EDGE_VALUE_SEQUENCE] = ""
        result[NpNode.IS_ROOT] = True
        result[NpNode.HAS_SUFFIX_LINK] = True
        return result

    def createInternalNode(self, parentPK, iEVS):
        result = self.nodeData[next(self.internalIdGenerator),]
        result[NpNode.INTERNAL_EDGE_VALUE_SEQUENCE] = iEVS
        result[NpNode.PARENT_LINK] = parentPK
        self.suffixLinker.nodeNeedsSuffixLink(result)
        result.isInternalNode = True
        return result

    def createLeafEdge(self, PK, value, dsOffset):
        result = self.nodeData[PK]
        result[NpNode.PK] = PK
        result[NpNode.INTERNAL_EDGE_START_OFFSET] = dsOffset
        result[NpNode.SUFFIX_OFFSET] = next(self.suffixGenerator)
        result[NpNode.IS_LEAF_EDGE] = True
        return result

    def createInternalEdge(self, parentPK, SK, targetPK):
        result = self.nodeData[parentPK]
        result.tN = targetPK
        result.isInternalEdge = True
        return result



