class SuffixLinker:
    def __init__(self):
        self.nodeNeedingSuffixLink = None

    def nodeNeedsSuffixLink(self, node):
        self.setLink(node)
        self.nodeNeedingSuffixLink = node

    def setLink(self, node):
        if self.nodeNeedingSuffixLink != None:
            self.nodeNeedingSuffixLink.sL = node.PK
            self.nodeNeedingSuffixLink = None
