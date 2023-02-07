import TreeContainment
import networkx as nx
import TreeContainmentTools
import graphviz


def network_color_image(graph, coloring):
    ni = graphviz.Digraph("DefinitionNetwork")

    # Setting colors and shapes for nodes
    for node in graph:
        name = str(node)
        color = ['red', 'green', 'blue', 'orange', 'purple'][coloring[node]]
        ni.node(str(node), name, color=color)

    # Adding all edges
    for edge in graph.edges:
        ni.edge(str(edge[0]), str(edge[1]))

    ni.render(directory='doctest-output', view=True)
    return

"""ENTER VALUES HERE"""
edges = [("Graph", "Tree"), ("Graph", "Display graph (3.2)"), ("Tree", "Display graph (3.2)"), ("Graph", "Embedding (3.3)"), ("Tree", "Embedding (3.3)"), ("Iso-labelling (3.7)", "Containment structure (3.8)"),
                 ("Compact (3.11)", "Super-compact (5.1)"), ("Display graph (3.2)", "Iso-labelling (3.7)"), ("Signature (3.9)", "Compact (3.11)"), ("Embedding (3.3)", "Containment structure (3.8)"), ("Display graph (3.2)", "Containment structure (3.8)"), ("Signature (3.9)", "Redundancy (3.10)"),
                 ("Containment structure (3.8)", "Signature (3.9)"), ("Redundancy (3.10)", "Compact restriction (3.12)"), ("Signature (3.9)", "Signature isomorphisms (7.1)"), ("Containment structure (3.8)", "Reconciliation (3.13)"), ("Path-decomposition (3.4)", "Tree-decomposition (3.5)"),
                 ("Tree-decomposition (3.5)", "Nice Tree-decomposition (3.6)"), ("Graph", "Path-decomposition (3.4)"), ("Graph", "Binary phylogenetic network (3.1)"),
                 ("Graph", "Path"), ("Path", "Path-decomposition (3.4)"), ("Compact (3.11)", "Compact restriction (3.12)")
                 ]
coloring = {"Tree": 0, "Graph": 0, "Display graph (3.2)": 1, "Embedding (3.3)": 1, "Iso-labelling (3.7)": 2, "Signature (3.9)": 2, "Compact (3.11)": 2, "Super-compact (5.1)": 3, "Redundancy (3.10)": 2, "Compact restriction (3.12)": 2,
                 "Containment structure (3.8)": 2, "Signature isomorphisms (7.1)": 3, "Reconciliation (3.13)": 2, "Tree-decomposition (3.5)": 1, "Path-decomposition (3.4)": 1, "Nice Tree-decomposition (3.6)": 1, "Binary phylogenetic network (3.1)": 1,
                 "Path": 0}

# edges = [("Graph", "Tree"), ("Graph", "Display graph"), ("Tree", "Display graph"), ("Graph", "Embedding"), ("Tree", "Embedding"), ("Iso-labelling", "Containment structure"),
#                  ("Compact", "Super-compact"), ("Display graph", "Iso-labelling"), ("Signature", "Compact"), ("Embedding", "Containment structure"), ("Display graph", "Containment structure"), ("Signature", "Redundancy"),
#                  ("Containment structure", "Signature"), ("Redundancy", "Compact restriction"), ("Signature", "Signature isomorphisms"), ("Containment structure", "Reconciliation"), ("Path-decomposition", "Tree-decomposition"),
#                  ("Tree-decomposition", "Nice tree-decomposition"), ("Graph", "Path-decomposition"), ("Graph", "Binary phylogenetic network"),
#                  ("Graph", "Path"), ("Path", "Path-decomposition"), ("Compact", "Compact restriction")
#                  ]
# coloring = {"Tree": 0, "Graph": 0, "Display graph": 1, "Embedding": 1, "Iso-labelling": 2, "Signature": 2, "Compact": 2, "Super-compact": 3, "Redundancy": 2, "Compact restriction": 2,
#                  "Containment structure": 2, "Signature isomorphisms": 3, "Reconciliation": 2, "Tree-decomposition": 1, "Path-decomposition": 1, "Nice tree-decomposition": 1, "Binary phylogenetic network": 1,
#                  "Path": 0}
# edges = [("Graph", "Tree"), ("Graph", "Network"), ("Network", "Display graph"), ("Tree", "Display graph"), ("Network", "Embedding"), ("Tree", "Embedding"), ("Iso-labelling", "Containment structure"),
#                  ("Compact", "Super-compact"), ("Display graph", "Iso-labelling"), ("Signature", "Compact"), ("Embedding", "Containment structure"), ("Display graph", "Containment structure"), ("Signature", "Redundancy"),
#                  ("Containment structure", "Signature"), ("Redundancy", "Restriction"), ("Signature", "Signature isomorphisms"), ("Containment structure", "Reconciliation"), ("Path-decomposition", "Tree-decomposition"),
#                  ("Path-decomposition", "Nice-decomposition"), ("Tree-decomposition", "Nice-decomposition"), ("Graph", "Path-decomposition"), ("Graph", "Phylogenetic Graph"), ("Graph", "Binary Graph")
#                  ]
# coloring = {"Graph": 0, "Tree": 1, "Network": 1, "Display graph": 3, "Embedding": 2, "Iso-labelling": 3, "Signature": 3, "Compact": 3, "Super-compact": 4, "Redundancy": 3, "Restriction": 3,
#                  "Containment structure": 3, "Signature isomorphisms": 4, "Reconciliation": 3, "Tree-decomposition": 1, "Path-decomposition": 1, "Nice-decomposition": 1, "Phylogenetic Graph": 1,
#                  "Binary Graph": 1}


graph = nx.DiGraph(edges)



network_color_image(graph, coloring)

