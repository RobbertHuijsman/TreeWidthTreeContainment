import networkx as nx
import itertools

import TreeContainmentTools


def descendant_in_dict_generator(network_in, tree_in):
    """Creates the descendant_dict and the depth_dict"""
    # Find the maximum depths of all nodes in the input network and find their descendants
    distance_dict = {}

    # Do network nodes

    # Find leaves
    todo_list_tree = []
    todo_list_network = []
    for node in tree_in.nodes():
        if node in network_in:
            distance_dict[node] = {}
            for parent in network_in.predecessors(node):
                todo_list_network.append(parent)
            for parent in tree_in.predecessors(node):
                todo_list_tree.append(parent)

    # Loop to find all network nodes
    while todo_list_network:
        node = todo_list_network.pop()
        if all(child in distance_dict for child in network_in.successors(node)):
            distance_dict[node] = {}
            for child in network_in.successors(node):

                # Add distance
                for key in distance_dict[child]:
                    if key in distance_dict[node]:
                        if distance_dict[node][key] < distance_dict[child][key] + 1:
                            distance_dict[node][key] = distance_dict[child][key] + 1
                    else:
                        distance_dict[node][key] = distance_dict[child][key] + 1
                if child not in distance_dict[node]:
                    distance_dict[node][child] = 1

            for parent in network_in.predecessors(node):
                todo_list_network.append(parent)

    # Do tree nodes
    while todo_list_tree:
        node = todo_list_tree.pop()
        if all(child in distance_dict for child in tree_in.successors(node)):
            distance_dict[node] = {}
            for child in tree_in.successors(node):
                # Add distance
                if child not in distance_dict[node]:
                    distance_dict[node][child] = 1
                for key in distance_dict[child]:
                    if key in distance_dict[node]:
                        if distance_dict[node][key] < distance_dict[child][key] + 1:
                            distance_dict[node][key] = distance_dict[child][key] + 1
                    else:
                        distance_dict[node][key] = distance_dict[child][key] + 1

            for parent in tree_in.predecessors(node):
                todo_list_tree.append(parent)

    # print(f"distance_dict = {distance_dict}")
    # Create the grandparent dict
    # grandparent_dict = {node: [grandchild1, grandchild2,...],...}
    grandparent_dict = {}
    for node1 in distance_dict:
        grandparent_dict[node1] = []
        for node2 in distance_dict[node1]:
            if distance_dict[node1][node2] == 2:
                grandparent_dict[node1].append(node2)

    # Add the maximums:
    for node1 in distance_dict:
        maximum = 0
        for node2 in distance_dict[node1]:
            if distance_dict[node1][node2] > maximum:
                maximum = distance_dict[node1][node2]
        distance_dict[node1]["max_distance"] = maximum

    return distance_dict, grandparent_dict


def descendant_check(signature, distance_in_dict, grandparent_in_dict):
    """"Depth is defined as the longest distance to a leaf"""
    # print("descendant check")
    # print(f"descendant_in_dict = {descendant_in_dict}")
    # print(f"depth_in_dict = {depth_in_dict}")

    # distance_dict = {node: {iso-label: distance,...},...}

    # NETWORK
    # Find the maximum depths of all nodes in the input network and find their descendants
    depth_dict = {}
    distance_dict = {}

    # Initiate lists
    todo_list_tree = []
    todo_list_network = []

    # Find the parents of leaves and enter leaves in the descendant_dict
    for node in signature.network.nodes():
        if signature.network.out_degree(node) == 0:
            distance_dict[node] = {}
            depth_dict[node] = 0
            for parent in signature.network.predecessors(node):
                todo_list_network.append(parent)

    # Loop to find all network nodes
    count = 0  # Used to check for loops
    max_count = signature.network.number_of_nodes()
    todo_list_network = list(set(todo_list_network))  # Removes duplicates

    while todo_list_network:
        node = todo_list_network.pop()
        if node in distance_dict:
            continue
        # Only process if all children have been processed already
        if all(child in distance_dict for child in signature.network.successors(node)):
            if count > max_count:
                # print("Too many iterations (network)")
                return False
            count += 1
            distance_dict[node] = {}
            node_label = signature.iso_labelling[node]
            for child in signature.network.successors(node):

                # Add distances from child
                for key in distance_dict[child]:
                    if key in distance_dict[node]:
                        if distance_dict[node][key] < distance_dict[child][key] + 1:
                            distance_dict[node][key] = distance_dict[child][key] + 1
                    else:
                        distance_dict[node][key] = distance_dict[child][key] + 1
                # Add distance to child
                if not (signature.iso_labelling[child] == "FUTURE" or signature.iso_labelling[child] == "PAST"):
                    if signature.iso_labelling[child] not in distance_dict[node]:  # To make sure there isn't another distance to child > 1
                        distance_dict[node][signature.iso_labelling[child]] = 1

                # Add depth
                if node not in depth_dict:
                    depth_dict[node] = depth_dict[child] + 1
                else:
                    if depth_dict[node] < depth_dict[child] + 1:
                        depth_dict[node] = depth_dict[child] + 1
            if not (node_label == "FUTURE" or node_label == "PAST"):

                # Check descendants
                for key_label in distance_dict[node]:
                    if key_label not in distance_in_dict[node_label]:
                        # print(f"[Descendant check]: {signature.iso_labelling[node]} has descendant {key_label} (network)")
                        return False

                    # Check distance
                    if distance_dict[node][key_label] > distance_in_dict[node_label][key_label]:
                        # print(f"[Distance check] {node_label} and {key_label} too large (network)")
                        return False

                # Check depth
                if depth_dict[node] > distance_in_dict[signature.iso_labelling[node]]["max_distance"]:
                    # print(f"[Depth check] node: {signature.iso_labelling[node]} with depth {depth_dict[node]} (network)")
                    return False

                # Check grandparents
                for key_label in grandparent_in_dict[node_label]:
                    if key_label in signature.inverse_iso_labelling:
                        if key_label not in distance_dict[node]:
                            # print(f"[Grandparent check] {node} with iso-label {node_label} and grandchild {key_label}")
                            return False

            for parent in signature.network.predecessors(node):
                todo_list_network.append(parent)

    if len(depth_dict) < signature.network.number_of_nodes():
        # print("[Loop check] (network)")
        return False

    # TREE
    # Find the maximum depths of all nodes in the tree and find their descendants
    depth_dict = {}
    distance_dict = {}

    # Initiate lists
    todo_list_tree = []
    todo_list_network = []

    # Find the parents of leaves and enter leaves in the descendant_dict
    for node in signature.tree.nodes():
        if signature.tree.out_degree(node) == 0:
            distance_dict[node] = {}
            depth_dict[node] = 0
            for parent in signature.tree.predecessors(node):
                todo_list_tree.append(parent)

    # Loop to find all tree nodes
    count = 0  # Used to check for loops
    max_count = signature.tree.number_of_nodes()
    todo_list_tree = list(set(todo_list_tree))  # Removes duplicates

    while todo_list_tree:
        node = todo_list_tree.pop()
        if node in distance_dict:
            continue
        # Only process if all children have been processed already
        if all(child in distance_dict for child in signature.tree.successors(node)):
            if count > max_count:
                # print("Too many iterations (tree)")
                return False
            count += 1
            distance_dict[node] = {}
            node_label = signature.iso_labelling[node]
            for child in signature.tree.successors(node):

                # Add distances from child
                for key in distance_dict[child]:
                    if key in distance_dict[node]:
                        if distance_dict[node][key] < distance_dict[child][key] + 1:
                            distance_dict[node][key] = distance_dict[child][key] + 1
                    else:
                        distance_dict[node][key] = distance_dict[child][key] + 1
                # Add distance to child
                if not (signature.iso_labelling[child] == "FUTURE" or signature.iso_labelling[child] == "PAST"):
                    if signature.iso_labelling[child] not in distance_dict[node]:  # To make sure there isn't another distance to child > 1
                        distance_dict[node][signature.iso_labelling[child]] = 1

                # Add depth
                if node not in depth_dict:
                    depth_dict[node] = depth_dict[child] + 1
                else:
                    if depth_dict[node] < depth_dict[child] + 1:
                        depth_dict[node] = depth_dict[child] + 1

            if not (node_label == "FUTURE" or node_label == "PAST"):
                # Check descendants
                for key_label in distance_dict[node]:
                    if key_label not in distance_in_dict[node_label]:
                        # print(f"Incorrect descendant: {signature.iso_labelling[node]} has descendant {label} (network)")
                        return False

                    # Check distance
                    if distance_dict[node][key_label] > distance_in_dict[node_label][key_label]:
                        # print(f"Distance between {node_label} and {key_label} too large (distance check tree)")
                        return False

                # Check depth
                if depth_dict[node] > distance_in_dict[signature.iso_labelling[node]]["max_distance"]:
                    # print(f"Incorrect depth! node: {signature.iso_labelling[node]} with depth {depth_dict[node]} (tree)")
                    return False

                # Check grandparents
                for key_label in grandparent_in_dict[node_label]:
                    if key_label in signature.inverse_iso_labelling:
                        if key_label not in distance_dict[node]:
                            # print(f"Failed grandparent check by node {node} with iso-label {node_label} and grandchild {key_label} (tree)")
                            return False

            for parent in signature.tree.predecessors(node):
                todo_list_tree.append(parent)

    if len(depth_dict) < signature.tree.number_of_nodes():
        # print("Loop (tree)")
        return False

    return True


def neighbor_in_dict_generator(graph):
    neighbor_in_dict = {}
    for node in graph:
        # Initiate tuples of lists of neighbors for each node (parents, children)
        neighbor_in_dict[node] = (set(graph.predecessors(node)), set(graph.successors(node)))
    return neighbor_in_dict


def neighbor_check(signature, neighbor_in_dict):
    """Check for tree nodes that checks direct adjacency"""
    for node in signature.tree.nodes():
        # Success becomes true if the nodes neighbors are confirmed from tree_in
        success = False

        # Initiate lists of parents and children iso-labels
        labelled_parent_set = set()
        for parent in signature.tree.predecessors(node):
            if signature.iso_labelling[parent] != "FUTURE" and signature.iso_labelling[parent] != "PAST":
                labelled_parent_set.add(signature.iso_labelling[parent])
        labelled_child_set = set()
        for child in signature.tree.successors(node):
            if signature.iso_labelling[child] != "FUTURE" and signature.iso_labelling[child] != "PAST":
                labelled_child_set.add(signature.iso_labelling[child])

        # Check if lists are contained in the specified neighbor_in_dict tuples of lists
        if signature.iso_labelling[node] != "FUTURE" and signature.iso_labelling[node] != "PAST":
            tuple_of_sets = neighbor_in_dict[signature.iso_labelling[node]]
            if labelled_parent_set.issubset(tuple_of_sets[0]):
                if labelled_child_set.issubset(tuple_of_sets[1]):
                    success = True

        else:
            # Check if lists are contained in one of the neighbor_in_dict tuples of lists
            for key in neighbor_in_dict:
                # Check if we're not comparing to an existing iso-label
                if key not in signature.inverse_iso_labelling:
                    tuple_of_sets = neighbor_in_dict[key]
                    if labelled_parent_set.issubset(tuple_of_sets[0]):
                        if labelled_child_set.issubset(tuple_of_sets[1]):
                            success = True
                            break

        if not success:
            return False

    return True


def correctness_check(signature):
    """This checks the signatures for correctness."""

    # Checking for PAST next to FUTURE. Necessary to prevent root edgecases
    for node in signature.tree.nodes():
        # Non-leaf
        if node not in signature.network:
            if signature.iso_labelling[node] == "PAST":
                for neighbor in itertools.chain(signature.tree.predecessors(node), signature.tree.successors(node)):
                    if signature.iso_labelling[neighbor] == "FUTURE":
                        # print("ERROR: iso-label FUTURE next to iso-label PAST")
                        return False
    for node in signature.network.nodes():
        # Non-leaf
        if node not in signature.tree:
            if signature.iso_labelling[node] == "PAST":
                for neighbor in itertools.chain(signature.network.predecessors(node), signature.network.successors(node)):
                    if signature.iso_labelling[neighbor] == "FUTURE":
                        # print("ERROR: iso-label FUTURE next to iso-label PAST")
                        return False

    # Checking for proper network structure
    for node in signature.network.nodes():
        if signature.network.in_degree(node) + signature.network.out_degree(node) > 3:
            # print(f"ERROR: Node {node} has degree {signature.network.in_degree(node) + signature.network.out_degree(node)}")
            return False

    # Checking for proper tree structure
    for node in signature.tree.nodes():
        if signature.tree.in_degree(node) > 1:
            # print(f"ERROR: Tree node {node} has in_degree {signature.tree.in_degree(node)}")
            return False

    # Checking for proper embeddings
    for node in signature.network.nodes():
        if node in signature.embedding.inverse_node_dict:
            # No reticulation node embeddings
            if signature.network.in_degree(node) > 1:
                # print(f"ERROR: Node {node} is an embedding with in_degree {signature.network.in_degree(node)}")
                return False
            # No embedding nodes with adjacent non-embedding edges
            for parent in signature.network.predecessors(node):
                if (parent, node) not in signature.embedding.inverse_edge_dict:
                    # print(f"ERROR: Node {node} is an embedding but {(parent, node)} is not an embedding edge")

                    return False
            for child in signature.network.successors(node):
                if (node, child) not in signature.embedding.inverse_edge_dict:
                    # print(f"ERROR: Node {node} is an embedding but {(node, child)} is not an embedding edge")
                    # if 'f' in signature.inverse_iso_labelling:
                    #     TreeContainmentTools.signature_image(signature, 1337)
                    #     x = 1 / 0
                    return False

    # Check for redundant non-embedding edges
    for edge in signature.network.edges():
        if edge not in signature.embedding.inverse_edge_dict:
            if signature.iso_labelling[edge[0]] == signature.iso_labelling[edge[1]]:
                # print(f"ERROR: redundant non-embedding edge {edge}")
                return False

    # Checking for matching edge embedding + inverse edge embeddings
    for edge in signature.embedding.edge_dict:
        for path_edge in signature.embedding.edge_dict[edge]:
            if path_edge not in signature.embedding.inverse_edge_dict:
                # print(f"ERROR: Embedding edge {edge} has a path_edge {path_edge} that is not in the inverse embedding")
                return False

    return True


def quantity_check(signature, network_in, tree_in):
    """This functions performs various checks based on quantities of nodes. It is mostly useful on small examples."""
    if signature.network.number_of_nodes() > network_in.number_of_nodes():
        # print(f"Too many network nodes")
        return False
    if signature.tree.number_of_nodes() > tree_in.number_of_nodes():
        # print(f"Too many tree nodes")
        return False
    if len(signature.embedding.inverse_node_dict) > tree_in.number_of_nodes():
        # print(f"Too many embedding nodes")
        return False
    # Number of non-embedding nodes in network cannot be bigger than the difference between number of network nodes and number of tree nodes
    if signature.network.number_of_nodes() - len(signature.embedding.inverse_node_dict) > network_in.number_of_nodes() - tree_in.number_of_nodes():
        # print(f"Too many non-embedding nodes")
        return False
    # Number of non-embedding tree nodes in the network cannot be bigger than half the difference between the number of network nodes and the number of tree nodes
    non_embedding_tree_nodes = 0
    reticulation_nodes = 0
    for node in signature.network.nodes():
        if node not in signature.embedding.inverse_node_dict:
            if signature.network.out_degree() == 2:
                non_embedding_tree_nodes += 1
            if signature.network.in_degree() == 2:
                reticulation_nodes += 1

    if non_embedding_tree_nodes > (network_in.number_of_nodes() - tree_in.number_of_nodes()) / 2:
        # print(f"Too many non-embedding tree nodes")
        return False

    if reticulation_nodes > (network_in.number_of_nodes() - tree_in.number_of_nodes()) / 2:
        # print(f"Too many reticulation nodes")
        return False

    return True


def sibling_in_dict_generator(network_in):
    sibling_in_dict = {"parent_side": {}, "child_side": {}}

    for node in network_in:
        if network_in.in_degree(node) == 2:
            parents = list(network_in.predecessors(node))
            # We only need it 1 way
            sibling_in_dict["child_side"][parents[0]] = parents[1]
        if network_in.out_degree(node) == 2:
            children = list(network_in.successors(node))
            # if it's already in the other dict, we still want it in this one
            # We only need it 1 way
            sibling_in_dict["parent_side"][children[0]] = children[1]

    return sibling_in_dict


def sibling_check(signature, sibling_in_dict):
    """sibling_in_dict is a dict with keys that are node and values that are tuples with the node's siblings"""

    # Find siblings
    for iso_label in signature.inverse_iso_labelling:
        if iso_label in sibling_in_dict["parent_side"]:
            if sibling_in_dict["parent_side"][iso_label] not in signature.inverse_iso_labelling:
                continue
            sibling1 = signature.inverse_iso_labelling[iso_label]
            sibling2 = signature.inverse_iso_labelling[sibling_in_dict["parent_side"][iso_label]]
            found = False
            for parent in signature.network.predecessors(sibling1):
                for sibling_candidate in signature.network.successors(parent):
                    if sibling_candidate == sibling2:
                        found = True
            if not found:
                # print("Sibling check failed")
                return False
        if iso_label in sibling_in_dict["child_side"]:
            if sibling_in_dict["child_side"][iso_label] not in signature.inverse_iso_labelling:
                continue
            sibling1 = signature.inverse_iso_labelling[iso_label]
            sibling2 = signature.inverse_iso_labelling[sibling_in_dict["child_side"][iso_label]]
            found = False
            for child in signature.network.successors(sibling1):
                for sibling_candidate in signature.network.predecessors(child):
                    if sibling_candidate == sibling2:
                        found = True
            if not found:
                # print("Sibling check failed")
                return False


    return True


def grandparent_in_dict_generator(network_in):
    grandparent_in_dict = {}

    for node in network_in:
        if network_in.in_degree(node) == 0:
            continue

            parents = list(network_in.predecessors(node))
            # We only need it 1 way
            sibling_in_dict["child_side"][parents[0]] = parents[1]
        if network_in.out_degree(node) == 2:
            children = list(network_in.successors(node))
            # if it's already in the other dict, we still want it in this one
            # We only need it 1 way
            sibling_in_dict["parent_side"][children[0]] = children[1]

    return sibling_in_dict


