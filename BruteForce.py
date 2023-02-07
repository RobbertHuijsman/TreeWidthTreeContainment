import networkx as nx
import TreeDecomposition
import NetworkxTreeIsomorphism as ni

def compact_node(network, node):
    """This function takes a node with indegree-1 and outdegree-1 and compacts it.
    Warning: it does not check if the node has indegree-1 and oudegree-1."""
    parent = tuple(network.predecessors(node))[0]
    child = tuple(network.successors(node))[0]

    # Edgecase where the parent and child are already connected!
    if (parent, child) in network.edges():
        network.remove_edge(parent, node)
        network.remove_edge(node, child)
        network.remove_node(node)
        compact_node(network, parent)
        compact_node(network, child)
    # Non edgecase
    else:
        network.remove_edge(parent, node)
        network.remove_edge(node, child)
        network.remove_node(node)
        network.add_edge(parent, child)


def brute_force(tree_in, network_in):

    # Create attribute dict for later comparisons:
    # Iso_labelling:
    leaf_dict_tree = {}
    leaf_dict_network = {}
    for node in tree_in:
        if tree_in.out_degree(node) == 0:
            leaf_dict_tree[node] = str(node)
        else:
            leaf_dict_tree[node] = 0
    for node in network_in:
        if network_in.out_degree(node) == 0:
            leaf_dict_network[node] = str(node)
        else:
            leaf_dict_network[node] = 0

    nx.set_node_attributes(tree_in, leaf_dict_tree, name="leaves")
    nx.set_node_attributes(network_in, leaf_dict_network, name="leaves")

    todo_list = [network_in]

    reticulation_list = []
    for node in network_in:
        if network_in.in_degree(node) == 2:
            reticulation_list.append(node)

    while todo_list:
        network = todo_list.pop()
        node = None
        for test_node in network:
            if network.in_degree(test_node) == 2:
                node = test_node
                break
        if node is None:
            isomorphism = ni.rooted_tree_isomorphism(tree_in, "rootT", network, "rootN")
            if not isomorphism:
                continue
            return True, isomorphism

            # DI = nx.algorithms.isomorphism.DiGraphMatcher(network, tree_in, node_match=lambda n1, n2: n1['leaves'] == n2['leaves'])
            # if not DI.is_isomorphic():
            # print("Positive")
            # print(f"Mapping: {DI.mapping}")
            # return True, DI.mapping

        else:
            for parent in network.predecessors(node):
                copy_network = network.copy()
                copy_network.remove_edge(parent, node)
                compact_node(copy_network, node)
                if copy_network.out_degree(parent) == 1:  # Parent was a tree node before
                    compact_node(copy_network, parent)
                else:
                    # If the parent was a reticulation node before, we need to remove it entirely and fix its parents
                    fix_list = [parent]
                    while fix_list:
                        fix_node = fix_list.pop()
                        if copy_network.out_degree(fix_node) == 1:
                            compact_node(copy_network, fix_node)
                        else:
                            if fix_node not in copy_network:
                                # A node can be added to the list twice if both children are fixed. Just ignore it.
                                continue
                            for fix_parent in copy_network.predecessors(fix_node):
                                fix_list.append(fix_parent)
                            copy_network.remove_node(fix_node)

                todo_list.append(copy_network)
    # print("Negative")
    return False, None
