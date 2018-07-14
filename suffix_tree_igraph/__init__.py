"""Suffix tree builder using igraph for holding tree.

Model is:

- Root Node properties:
    Node suffix_link
    Dict children<Value, Node>

- Internal Node properties:
    Node suffix_link
    Node parent
    Dict children<Value, Node>
    IESO - incoming edge start offset
    IEEO - incoming edge end offset

- Leaf Node properties:
    Node parent
    IESO - incoming edge start offset

To convert parent-child relationship to igraph:

1. parallel implementations: add graph construction in parallel with the existing model

    Root -> create graph, add vertex 0
    Leaf -> add vertex and edge _from/_to
    Internal -> add vertex between _from and _to,
                add edges _from-(new), (new)-_to,
                remove edge _from-_to

2. adjust traversal to use igraph structure

3. remove original implementation

"""