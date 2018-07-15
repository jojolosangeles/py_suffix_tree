from suffix_tree_igraph.igraph_adapter import igraph_add_suffix_link


class SuffixLinker:

    def __init__(self):
        self.node_missing_suffix_link = None

    def needs_suffix_link(self, node_id):
        """Any newly created internal node needs a suffix link.  If a previously
        created node is missing its suffix link, then it just points
        to this node."""
        self.link_to(node_id)
        self.node_missing_suffix_link = node_id

    def link_to(self, node_id):
        if self.node_missing_suffix_link != None:
            igraph_add_suffix_link(self.node_missing_suffix_link, node_id)
        self.node_missing_suffix_link = None