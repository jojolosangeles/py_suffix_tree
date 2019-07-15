class SuffixLinker:

    def __init__(self):
        self.node_missing_suffix_link = None
        self.needed = []
        self.got = []

    def needs_suffix_link(self, node):
        print(f"{id(node)} {node.PK} needs a Suffix Link, previous was: {self.node_missing_suffix_link}")
        """Any newly created internal node needs a suffix link.  If a previously
        created node is missing its suffix link, it points to a newly created node."""
        assert(node != self.node_missing_suffix_link)
        self.needed.append(node.PK)
        self.link_to(node)
        self.node_missing_suffix_link = node
        print(f"node missing suffix link is: {node.PK}")

    def link_to(self, node):
        if self.node_missing_suffix_link != None:
            print(f"{id(self.node_missing_suffix_link)} {self.node_missing_suffix_link.PK} getting a Suffix Link to {id(node)} {node}")
            self.node_missing_suffix_link.suffixLink = node
            self.got.append(self.node_missing_suffix_link.PK)
        self.node_missing_suffix_link = None

    def __repr__(self):
        return f"Need {len(self.needed) - len(self.got)}: {self.needed}, Got: {self.got}"