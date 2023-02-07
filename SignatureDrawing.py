import TreeContainment
import networkx as nx
import TreeContainmentTools
import TreeDecomposition

"""ENTER SIGNATURE VALUES HERE"""
tree_edges = [(4, 3)]
network_edges = [(1, 2), (2, 3)]
node_dict = {4: 1, 3: 3}  # Embedding node mapping. int : int
edge_dict = {(4, 3): [(1, 2), (2, 3)]}  # Embedding edge mapping. tuple(int) : list(tuple(int))
iso_labelling = {1: "a", 2: "PAST", 3: "PAST", 4: "PAST"}

tree = nx.DiGraph(tree_edges)
network = nx.DiGraph(network_edges)

inverse_node_dict = {v: k for k, v in node_dict.items()}

inverse_edge_dict = {}
for edge in edge_dict:
    for path_edge in edge_dict[edge]:
        inverse_edge_dict[path_edge] = edge

embedding = TreeContainment.Embedding(node_dict, edge_dict, inverse_node_dict, inverse_edge_dict)

inverse_iso_labelling = {v: k for k, v in iso_labelling.items()}

draw_signature = TreeContainment.Signature(tree, network, embedding, iso_labelling, inverse_iso_labelling, 99)
TreeContainmentTools.signature_image(draw_signature, 0)

"""ENTER INPUT DISPLAY GRAPH VALUES HERE"""
# network_edge_list = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("b", "e"), ("d", "f"), ("c", "g")]
# tree_edge_list = []
#
# network_edge_list = [("rootT", "g"), ("g", "h"), ("h", "a"), ("h", "b"), ("g", "i"), ("i", "j"), ("i", "f"), ("j", "c"), ("j", "k"), ("k", "d"), ("k", "e")]
# tree_edge_list = [("rootT", "k"), ("h", "e"), ("h", "f"), ("i", "g")]
# tree_edge_list = [("i", "h"), ("h", "e"), ("h", "f"), ("i", "g")]


network_edge_list = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("b", "e"), ("d", "f"), ("c", "g")]
tree_edge_list = [("i", "h"), ("h", "e"), ("h", "f"), ("i", "g")]

network_in = nx.DiGraph(network_edge_list)
tree_in = nx.DiGraph(tree_edge_list)

# tree_in.add_node("a")
# tree_in.add_node("b")
# tree_in.add_node("c")
# tree_in.add_node("d")
# tree_in.add_node("e")
# tree_in.add_node("f")

TreeDecomposition.display_graph_image(tree_in, network_in)

# Image 14
# tree_edges = [(6, 4), (6, 5), (7, 6), (8, 7)]
# network_edges = [(1, 2), (2, 3), (3, 4), (3, 5)]
# node_dict = {1: 8, 2: 7, 3: 6, 4: 4, 5: 5}  # Embedding node mapping. int : int
# edge_dict = {(6, 4): [(3, 4)], (6, 5): [(3, 5)], (7, 6): [(2, 3)], (8, 7): [(1, 2)]}  # Embedding edge mapping. tuple(int) : list(tuple(int))
# iso_labelling = {1: "rootN", 2: "a", 3: "b", 4: "FUTURE", 5: "FUTURE", 6: "FUTURE", 7: "FUTURE", 8: "FUTURE"}
#
# network_edge_list = [("rootN", "a"), ("a", "b"), ("b", "c"), ("b", "d"), ("a", "e")]
# tree_edge_list = [("rootT", "f"), ("f", "g"), ("g", "c"), ("g", "d"), ("f", "e")]

# Image 25
# network_edge_list = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("b", "e"), ("d", "f"), ("c", "g")]
# tree_edge_list = [("i", "h"), ("h", "e"), ("h", "f"), ("i", "g")]

# Image 30
# tree_edges = [(6, 5)]
# network_edges = [(1, 2), (2, 3), (2, 4), (4, 8), (8, 5), (3, 7), (3, 8)]
# node_dict = {1: 6, 5: 5}  # Embedding node mapping. int : int
# edge_dict = {(6, 5): [(1, 2), (2, 4), (4, 8), (8, 5)]}  # Embedding edge mapping. tuple(int) : list(tuple(int))
# iso_labelling = {1: "FUTURE", 2: "a", 3: "b", 4: "FUTURE", 5: "FUTURE", 6: "FUTURE", 7: "FUTURE", 8: "FUTURE"}
