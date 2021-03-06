class SuffixLinker:

    def __init__(self):
        self.node_missing_suffix_link = None

    def needs_suffix_link(self, node):
        """Any newly created internal node needs a suffix link.  If a previously
        created node is missing its suffix link, it points to a newly created node."""
        self.link_to(node)
        self.node_missing_suffix_link = node

    def link_to(self, node):
        if self.node_missing_suffix_link != None:
            self.node_missing_suffix_link.suffix_link = node
        self.node_missing_suffix_link = None