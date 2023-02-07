import networkx as nx
import time
import TreeContainmentTools
import TreewidthHeuristics
import graphviz
import itertools
import IsomorphismCheckSource
import TreeContainment
import TreeDecomposition
import matplotlib.pyplot as plt


def isomorphism_checker6(signature1, signature2):
    """This function checks whether two signatures are isomorphic.
    Used for general isomorphism checking in main_algorithm (to remove duplicate signatures)
    """
    # Initial quick checks (number of nodes)
    if signature1.tree.number_of_nodes() != signature2.tree.number_of_nodes():
        return False
    if signature1.network.number_of_nodes() != signature2.network.number_of_nodes():
        return False

    # More quick checks (number of edges)
    if signature1.tree.number_of_edges() != signature2.tree.number_of_edges():
        return False
    if signature1.network.number_of_edges() != signature2.network.number_of_edges():
        return False

    # Extra checks (embedding size)
    if len(signature1.embedding.node_dict) != len(signature2.embedding.node_dict):
        return False
    if len(signature1.embedding.edge_dict) != len(signature2.embedding.edge_dict):
        return False

    # Extra checks (present nodes are embeddings?)  TODO: experimental
    for node in signature1.network:
        label = signature1.iso_labelling[node]
        if label != "FUTURE" and label != "PAST":
            if node in signature1.embedding.inverse_node_dict and not signature2.inverse_iso_labelling[label] in signature2.embedding.inverse_node_dict or not node in signature1.embedding.inverse_node_dict and signature2.inverse_iso_labelling[label] in signature2.embedding.inverse_node_dict:
                return False

    # Making display graphs
    edge_list = []
    edge_list.extend(signature1.network.edges())
    edge_list.extend(signature1.tree.edges())
    display_graph1 = nx.DiGraph(edge_list)

    edge_list = []
    edge_list.extend(signature2.network.edges())
    edge_list.extend(signature2.tree.edges())
    display_graph2 = nx.DiGraph(edge_list)

    # Create attributes
    # Iso_labelling:
    nx.set_node_attributes(display_graph1, signature1.iso_labelling, name="iso_labelling")
    nx.set_node_attributes(display_graph2, signature2.iso_labelling, name="iso_labelling")

    # Embeddings nodes (add edges with attributes)
    nx.set_edge_attributes(display_graph1, 0, "embedding")
    for node in signature1.embedding.node_dict:
        display_graph1.add_edge(node, signature1.embedding.node_dict[node], embedding=1)

    nx.set_edge_attributes(display_graph2, 0, "embedding")
    for node in signature2.embedding.node_dict:
        display_graph2.add_edge(node, signature2.embedding.node_dict[node], embedding=1)

    # Embedding edges (add attributes to edges that are embeddings)
    for edge in signature1.embedding.inverse_edge_dict:
        display_graph1.add_edge(edge[0], edge[1], embedding=2)
    for edge in signature2.embedding.inverse_edge_dict:
        display_graph2.add_edge(edge[0], edge[1], embedding=2)

    DI = nx.algorithms.isomorphism.DiGraphMatcher(display_graph1, display_graph2, node_match=lambda n1, n2: n1['iso_labelling'] == n2['iso_labelling'], edge_match=lambda e1, e2: e1['embedding'] == e2['embedding'])

    if not DI.is_isomorphic():
        return False
    # print(DI.mapping)

    # if (1, 6) in signature1.network.edges() and \
    #         (1, 6) in signature2.network.edges() and \
    #         (6, 13) in signature1.network.edges() and \
    #         (6, 13) in signature2.network.edges() and \
    #         (7, 11) in signature1.tree.edges() and \
    #         (7, 11) in signature2.tree.edges():
    #     print("TESTTESTTEST")
    #     TreeContainmentTools.signature_image(signature1, 301)
    #     TreeContainmentTools.signature_image(signature2, 302)
    #     # TreeDecomposition.display_graph_image()
    #     print("TEST1")
    #     print(display_graph1.edges(data=True))
    #     print("TEST2")
    #     print(display_graph2.edges(data=True))
    #     print("TEST3")
    #     print(f"mapping = {DI.mapping}")
    #
    #
    #     # ni = graphviz.Digraph("Display Graph1")
    #     # # Setting shapes for nodes
    #     # for node in display_graph1:
    #     #     ni.node(str(node), str(node))
    #     #
    #     # # Adding all edges
    #     # for edge in display_graph1.edges:
    #     #     ni.edge(str(edge[0]), str(edge[1]))
    #     #
    #     # ni.render(directory='doctest-output', view=True)
    #     #
    #     # ni = graphviz.Digraph("Display Graph2")
    #     # # Setting shapes for nodes
    #     # for node in display_graph2:
    #     #     ni.node(str(node), str(node))
    #     #
    #     # # Adding all edges
    #     # for edge in display_graph2.edges:
    #     #     ni.edge(str(edge[0]), str(edge[1]))
    #     #
    #     # ni.render(directory='doctest-output', view=True)
    #     #
    #     #
    #     # # Leaf dictionaries
    #     # leaf_dict1 = {}
    #     # for node in signature1.tree:
    #     #     if node in signature1.network:
    #     #         leaf_dict1[node] = 1
    #     #     else:
    #     #         leaf_dict1[node] = 0
    #     # for node in signature1.network:
    #     #     if node not in signature1.tree:
    #     #         leaf_dict1[node] = 0
    #     #
    #     # leaf_dict2 = {}
    #     # for node in signature2.tree:
    #     #     if node in signature2.network:
    #     #         leaf_dict2[node] = 1
    #     #     else:
    #     #         leaf_dict2[node] = 0
    #     # for node in signature2.network:
    #     #     if node not in signature2.tree:
    #     #         leaf_dict2[node] = 0
    #     #
    #     # nx.set_node_attributes(display_graph1, leaf_dict1, name="leaves")
    #     # nx.set_node_attributes(display_graph2, leaf_dict2, name="leaves")
    #     #
    #     # DI = nx.algorithms.isomorphism.GraphMatcher(display_graph1, display_graph2,
    #     #                                             node_match=lambda n1, n2: n1['iso_labelling'] == n2[
    #     #                                                 'iso_labelling'] and n1["leaves"] == n2["leaves"],
    #     #                                             edge_match=lambda e1, e2: e1['embedding'] == e2['embedding'])
    #     #
    #     # if DI.is_isomorphic():
    #     #     print("TESTTESTTESTTESTTEST: True")
    #     #     print(DI.mapping)
    #     # else:
    #     #     print("TESTTESTTESTTESTTEST: False")
    #     #
    #     # print("TEST11")
    #     # print(display_graph1.nodes(data=True))
    #     # print("TEST12")
    #     # print(display_graph2.nodes(data=True))
    #     #
    #     # DI1 = nx.algorithms.isomorphism.GraphMatcher(signature1.tree, signature2.tree)
    #     # print(f"WTF: DI1.is_isomorphic(): {DI1.is_isomorphic()}")
    #     # print(DI1.mapping)
    #     # DI2 = nx.algorithms.isomorphism.GraphMatcher(signature1.network, signature2.network)
    #     # print(f"WTF: DI2.is_isomorphic(): {DI2.is_isomorphic()}")
    #     # print(DI2.mapping)
    #     iso_label_dict1 = nx.get_node_attributes(display_graph1, 'iso_labelling')
    #     embedding_dict1 = nx.get_edge_attributes(display_graph1, 'embedding')
    #     iso_label_dict2 = nx.get_node_attributes(display_graph2, 'iso_labelling')
    #     embedding_dict2 = nx.get_edge_attributes(display_graph2, 'embedding')
    #
    #     ni = graphviz.Digraph("Display Graph1")
    #     # Setting shapes for nodes
    #     for node in display_graph1:
    #         name = str(node)
    #         color = 'green'
    #         if iso_label_dict1[node] == "FUTURE":
    #             color = 'blue'
    #         elif iso_label_dict1[node] == "PAST":
    #             color = 'red'
    #         else:
    #             name = name + f" ({iso_label_dict1[node]})"
    #         ni.node(str(node), name, color=color)
    #
    #     # Adding all edges
    #     for edge in display_graph1.edges:
    #         if embedding_dict1[edge] == 1:
    #             ni.edge(str(edge[0]), str(edge[1]), color='purple')
    #         elif embedding_dict1[edge] == 0:
    #             ni.edge(str(edge[0]), str(edge[1]), arrowhead='empty')
    #         else:
    #             ni.edge(str(edge[0]), str(edge[1]))
    #
    #     ni.render(directory='doctest-output', view=True)
    #
    #     ni = graphviz.Digraph("Display Graph2")
    #     # Setting shapes for nodes
    #     for node in display_graph2:
    #         name = str(node)
    #         color = 'green'
    #         if iso_label_dict2[node] == "FUTURE":
    #             color = 'blue'
    #         elif iso_label_dict2[node] == "PAST":
    #             color = 'red'
    #         else:
    #             name = name + f" ({iso_label_dict2[node]})"
    #         ni.node(str(node), name, color=color)
    #
    #     # Adding all edges
    #     for edge in display_graph2.edges:
    #         if embedding_dict2[edge] == 1:
    #             ni.edge(str(edge[0]), str(edge[1]), color='purple')
    #         elif embedding_dict2[edge] == 0:
    #             ni.edge(str(edge[0]), str(edge[1]), arrowhead='empty')
    #         else:
    #             ni.edge(str(edge[0]), str(edge[1]))
    #
    #     ni.render(directory='doctest-output', view=True)
    #
    #
    #     print("TESTTESTTESTTESTTESTTESTTESTTEST")
    #
    #     # Display graphs
    #     original_edge_list1 = [(1, 6), (6, 12), (6, 13), (13, 10), (13, 12), (12, 9), (2, 7), (7, 9), (7, 11)]
    #     original_edge_list2 = [(1, 6), (6, 12), (6, 13), (13, 9), (13, 12), (12, 10), (2, 7), (7, 9), (7, 11)]
    #
    #     # Full graph with extra edges for embeddings:
    #     edge_list1 = [(2, 1), (2, 7), (1, 6), (7, 6), (7, 9), (7, 11), (6, 12), (6, 13), (13, 12), (13, 10), (11, 10),
    #                   (12, 9), (9, 9)]
    #     edge_list2 = [(2, 1), (2, 7), (1, 6), (7, 6), (7, 9), (7, 11), (6, 12), (6, 13), (13, 12), (13, 9), (11, 10),
    #                   (12, 10), (9, 9)]
    #
    #     graph1 = nx.DiGraph(edge_list1)
    #     graph2 = nx.DiGraph(edge_list2)
    #
    #     # embedding_dict1 = {(2, 1): 1, (2, 7): 0, (1, 6): 0, (7, 6), (7, 9), (7, 11), (6, 12), (6, 13), (13, 12), (13, 9), (11, 10), (12, 10), (9, 9)}
    #
    #     iso_label_dict1 = {1: "PAST", 2: "PAST", 6: "l", 7: "f", 9: "FUTURE", 10: "FUTURE", 11: "FUTURE", 12: "k",
    #                        13: "FUTURE"}
    #     iso_label_dict2 = {1: "PAST", 2: "PAST", 6: "l", 7: "f", 9: "FUTURE", 10: "FUTURE", 11: "FUTURE", 12: "k",
    #                        13: "FUTURE"}
    #
    #     # Embedding edges (add attributes to edges that are embeddings)
    #
    #     embedding_dict1 = {}
    #     for edge in edge_list1:
    #         if edge in original_edge_list1:
    #             if edge in [(1, 6), (6, 12), (6, 13), (12, 9), (13, 10)]:
    #                 embedding_dict1[edge] = 2
    #             else:
    #                 embedding_dict1[edge] = 0
    #         else:
    #             embedding_dict1[edge] = 1
    #     print(f"embedding_dict1 = {embedding_dict1}")
    #
    #     embedding_dict2 = {}
    #     for edge in edge_list2:
    #         if edge in original_edge_list2:
    #             if edge in [(1, 6), (6, 12), (6, 13), (13, 9), (12, 10)]:
    #                 embedding_dict2[edge] = 2
    #             else:
    #                 embedding_dict2[edge] = 0
    #         else:
    #             embedding_dict2[edge] = 1
    #     print(f"embedding_dict2 = {embedding_dict2}")
    #
    #     nx.set_node_attributes(graph1, iso_label_dict1, name="iso_labelling")
    #     nx.set_node_attributes(graph2, iso_label_dict2, name="iso_labelling")
    #
    #     nx.set_edge_attributes(graph1, embedding_dict1, name="embedding")
    #     nx.set_edge_attributes(graph2, embedding_dict2, name="embedding")
    #
    #     print(f"graph1.nodes(data=True) = {graph1.nodes(data=True)}")
    #     print(f"graph2.nodes(data=True) = {graph2.nodes(data=True)}")
    #
    #     print(f"graph1.edges(data=True) = {graph1.edges(data=True)}")
    #     print(f"graph2.edges(data=True) = {graph2.edges(data=True)}")
    #
    #     # DI = nx.algorithms.isomorphism.GraphMatcher(graph1, graph2)
    #     # DI = nx.algorithms.isomorphism.GraphMatcher(graph1, graph2, edge_match=lambda e1, e2: e1['embedding'] == e2['embedding'])
    #     DI = nx.algorithms.isomorphism.GraphMatcher(graph1, graph2,
    #                                                 node_match=lambda n1, n2: n1['iso_labelling'] == n2[
    #                                                     'iso_labelling'],
    #                                                 edge_match=lambda e1, e2: e1['embedding'] == e2['embedding'])
    #
    #     print(f"\nDI.is_isomorphic() = {DI.is_isomorphic()}")
    #     if DI.is_isomorphic():
    #         print(f"DI.mapping() = {DI.mapping()}")
    #
    #     graph3 = graph1
    #     graph1 = graph2.copy()
    #     graph2 = graph3.copy()
    #
    #     print(f"graph1 == display_graph1: {graph1 == display_graph1}")
    #     print(f"graph1 == display_graph2: {graph1 == display_graph2}")
    #     print(f"graph1 == display_graph1: {graph2 == display_graph1}")
    #     print(f"graph1 == display_graph1: {graph2 == display_graph2}")
    #
    #     print(f"graph1.edges() == display_graph1.edges(): {graph1.edges() == display_graph1.edges()}")
    #     print(f"graph2.edges() == display_graph2.edges(): {graph2.edges() == display_graph2.edges()}")
    #     print(f"graph1.nodes() == display_graph1.nodes(): {graph1.nodes() == display_graph1.nodes()}")
    #     print(f"graph2.nodes() == display_graph2.nodes(): {graph2.nodes() == display_graph2.nodes()}")
    #     print(f"graph1.edges(data=True) == display_graph1.edges(data=True): {graph1.edges(data=True) == display_graph1.edges(data=True)}")
    #     print(f"graph2.edges(data=True) == display_graph2.edges(data=True): {graph2.edges(data=True) == display_graph2.edges(data=True)}")
    #     print(f"graph1.nodes(data=True) == display_graph1.nodes(data=True): {graph1.nodes(data=True) == display_graph1.nodes(data=True)}")
    #     print(f"graph2.nodes(data=True) == display_graph2.nodes(data=True): {graph2.nodes(data=True) == display_graph2.nodes(data=True)}")
    #
    #     print(f"graph1.edges(data=True)  : {graph1.edges(data=True)}")
    #     print(f"display_graph1(data=True): {display_graph1.edges(data=True)}")
    #
    #     print(f"graph2.edges(data=True)  : {graph2.edges(data=True)}")
    #     print(f"display_graph2(data=True): {display_graph2.edges(data=True)}")
    #
    #
    #     print(f"graph1.edges(data=True).sort()  : {sorted([(2, 1, {'embedding': 1}), (2, 7, {'embedding': 0}), (1, 6, {'embedding': 2}), (7, 6, {'embedding': 1}), (7, 9, {'embedding': 0}), (7, 11, {'embedding': 0}), (6, 12, {'embedding': 2}), (6, 13, {'embedding': 2}), (9, 9, {'embedding': 1}), (11, 10, {'embedding': 1}), (12, 10, {'embedding': 2}), (13, 12, {'embedding': 0}), (13, 9, {'embedding': 2})])}")
    #     print(f"display_graph1(data=True).sort(): {sorted([(1, 6, {'embedding': 2}), (6, 12, {'embedding': 2}), (6, 13, {'embedding': 2}), (12, 10, {'embedding': 2}), (13, 9, {'embedding': 2}), (13, 12, {'embedding': 0}), (9, 9, {'embedding': 1}), (2, 7, {'embedding': 0}), (2, 1, {'embedding': 1}), (7, 9, {'embedding': 0}), (7, 11, {'embedding': 0}), (7, 6, {'embedding': 1}), (11, 10, {'embedding': 1})])}")
    #
    #
    #
    #     print(f"edges equal1?  : {sorted([(2, 1, {'embedding': 1}), (2, 7, {'embedding': 0}), (1, 6, {'embedding': 2}), (7, 6, {'embedding': 1}), (7, 9, {'embedding': 0}), (7, 11, {'embedding': 0}), (6, 12, {'embedding': 2}), (6, 13, {'embedding': 2}), (9, 9, {'embedding': 1}), (11, 10, {'embedding': 1}), (12, 10, {'embedding': 2}), (13, 12, {'embedding': 0}), (13, 9, {'embedding': 2})]) == sorted([(1, 6, {'embedding': 2}), (6, 12, {'embedding': 2}), (6, 13, {'embedding': 2}), (12, 10, {'embedding': 2}), (13, 9, {'embedding': 2}), (13, 12, {'embedding': 0}), (9, 9, {'embedding': 1}), (2, 7, {'embedding': 0}), (2, 1, {'embedding': 1}), (7, 9, {'embedding': 0}), (7, 11, {'embedding': 0}), (7, 6, {'embedding': 1}), (11, 10, {'embedding': 1})])}")
    #     print(f"edges equal2?  : {sorted([(2, 1, {'embedding': 1}), (2, 7, {'embedding': 0}), (1, 6, {'embedding': 2}), (7, 6, {'embedding': 1}), (7, 9, {'embedding': 0}), (7, 11, {'embedding': 0}), (6, 12, {'embedding': 2}), (6, 13, {'embedding': 2}), (9, 9, {'embedding': 1}), (11, 10, {'embedding': 1}), (12, 9, {'embedding': 2}), (13, 12, {'embedding': 0}), (13, 10, {'embedding': 2})]) == sorted([(1, 6, {'embedding': 2}), (6, 12, {'embedding': 2}), (6, 13, {'embedding': 2}), (12, 9, {'embedding': 2}), (13, 10, {'embedding': 2}), (13, 12, {'embedding': 0}), (9, 9, {'embedding': 1}), (2, 7, {'embedding': 0}), (2, 1, {'embedding': 1}), (7, 9, {'embedding': 0}), (7, 11, {'embedding': 0}), (7, 6, {'embedding': 1}), (11, 10, {'embedding': 1})])}")


    return True


def isomorphism_checker7(signature1, signature2):
    """This function checks whether two signatures are isomorphic.
    """

    # Initial quick checks (number of nodes)
    if signature1.tree.number_of_nodes() != signature2.tree.number_of_nodes():
        return False
    if signature1.network.number_of_nodes() != signature2.network.number_of_nodes():
        return False

    # More quick checks (number of edges)
    if signature1.tree.number_of_edges() != signature2.tree.number_of_edges():
        return False
    if signature1.network.number_of_edges() != signature2.network.number_of_edges():
        return False

    # Extra checks (embedding size)
    if len(signature1.embedding.node_dict) != len(signature2.embedding.node_dict):
        return False
    if len(signature1.embedding.edge_dict) != len(signature2.embedding.edge_dict):
        return False

    # Extra checks (present nodes are embeddings?)  TODO: experimental
    for node in signature1.network:
        label = signature1.iso_labelling[node]
        if label != "FUTURE" and label != "PAST":
            if node in signature1.embedding.inverse_node_dict and not signature2.inverse_iso_labelling[label] in signature2.embedding.inverse_node_dict or not node in signature1.embedding.inverse_node_dict and signature2.inverse_iso_labelling[label] in signature2.embedding.inverse_node_dict:
                return False

    # Making display graphs
    edge_list = []
    edge_list.extend(signature1.network.edges())
    edge_list.extend(signature1.tree.edges())
    display_graph1 = nx.DiGraph(edge_list)

    edge_list = []
    edge_list.extend(signature2.network.edges())
    edge_list.extend(signature2.tree.edges())
    display_graph2 = nx.DiGraph(edge_list)

    # Create attributes
    # Iso_labelling:
    iso_labelling_dict1 = {}
    for node in signature1.iso_labelling:
        if signature1.iso_labelling[node] == "FUTURE" or signature1.iso_labelling[node] == "PAST":
            iso_labelling_dict1[node] = 1
        else:
            iso_labelling_dict1[node] = signature1.iso_labelling[node]

    iso_labelling_dict2 = {}
    for node in signature2.iso_labelling:
        if signature2.iso_labelling[node] == "FUTURE" or signature2.iso_labelling[node] == "PAST":
            iso_labelling_dict2[node] = 1
        else:
            iso_labelling_dict2[node] = signature2.iso_labelling[node]

    nx.set_node_attributes(display_graph1, iso_labelling_dict1, name="iso_labelling")
    nx.set_node_attributes(display_graph2, iso_labelling_dict2, name="iso_labelling")

    # Embeddings nodes (add edges with attributes)
    nx.set_edge_attributes(display_graph1, 0, "embedding")
    for node in signature1.embedding.node_dict:
        display_graph1.add_edge(node, signature1.embedding.node_dict[node], embedding=1)

    nx.set_edge_attributes(display_graph2, 0, "embedding")
    for node in signature2.embedding.node_dict:
        display_graph2.add_edge(node, signature2.embedding.node_dict[node], embedding=1)

    # Embedding edges (add attributes to edges that are embeddings)
    for edge in signature1.embedding.inverse_edge_dict:
        display_graph1.add_edge(edge[0], edge[1], embedding=2)
    for edge in signature2.embedding.inverse_edge_dict:
        display_graph2.add_edge(edge[0], edge[1], embedding=2)


    # signature1.print()
    # signature2.print()
    # TreeContainmentTools.signature_image(signature1, 100)
    # TreeContainmentTools.signature_image(signature2, 101)

    # print(display_graph1.nodes(data=True))
    # print(display_graph2.nodes(data=True))
    # print(display_graph1.edges(data=True))
    # print(display_graph2.edges(data=True))

    DI = nx.algorithms.isomorphism.DiGraphMatcher(display_graph1, display_graph2, node_match=lambda n1, n2: n1['iso_labelling'] == n2['iso_labelling'], edge_match=lambda e1, e2: e1['embedding'] == e2['embedding'])
    # pos = nx.spring_layout(display_graph1, seed=225)  # Seed for reproducible layout
    # nx.draw(display_graph1, with_labels = True)
    # plt.show()

    if not DI.is_isomorphic():
        # print("Negative")
        return False
    # print(DI.mapping)
    # print("Positive")
    # TreeContainmentTools.signature_image(signature1, signature1.node_count + signature2.node_count + 100)
    # TreeContainmentTools.signature_image(signature2, signature1.node_count + signature2.node_count + 200)

    # print(f"Mapping: {DI.mapping}")

    return DI.mapping
