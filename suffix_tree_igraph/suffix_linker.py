

class SuffixLinker:
    def __init__(self, add_suffix_link_method):
        self.node_missing_suffix_link = None
        self.add_suffix_link_method = add_suffix_link_method

    def needs_suffix_link(self, node):
        """Any newly created internal node needs a suffix link.  If a previously
        created node is missing its suffix link, then it just points
        to this node."""
        self.link_to(node)
        self.node_missing_suffix_link = node

    def link_to(self, node):
        if self.node_missing_suffix_link != None:
            self.add_suffix_link_method(self.node_missing_suffix_link, node)
        self.node_missing_suffix_link = None