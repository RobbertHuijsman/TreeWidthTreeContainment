import networkx as nx
import itertools
import TreeDecomposition
import TreeContainmentTools
import NetworkIsomorphismTools
import random
import TreeContainmentChecks


def possible_type_check(signature, graph, node, z_in_tree):
    # This function checks which type the given node could be (could be multiple options)
    output_list = []
    if node in signature.embedding.node_dict:
        if signature.embedding.node_dict[node] == node:
            return ["leaf"]
    if graph.in_degree(node) == 0:
        output_list.append("root")
    if graph.in_degree(node) <= 1:
        output_list.append("tree")
    if not z_in_tree:
        if graph.out_degree(node) <= 1:
            output_list.append("reticulation")

    return output_list


def definite_type_check(graph_in, node):
    # This function checks which type the given node is in graph_IN
    if graph_in.in_degree(node) == 0:
        return "root"
    elif graph_in.out_degree(node) == 2:
        return "tree"
    elif graph_in.out_degree(node) == 0:
        return "leaf"
    else:
        return "reticulation"


def neighbor_possible_type_check(signature, graph, node, z_in_tree):
    # This function checks the types of the neighbors of a node
    parent_type_dict = {}
    child_type_dict = {}

    # Check types of neighbors in the graph
    # Parents
    for i, parent in enumerate(graph.predecessors(node)):
        output_list = []
        if graph.in_degree(parent) <= 1:
            output_list.append("tree")
            if graph.in_degree(parent) == 0:
                if parent in signature.embedding.inverse_node_dict or z_in_tree:
                    output_list.append("root")
        if not z_in_tree:
            if graph.out_degree(parent) <= 1:
                if parent not in signature.embedding.inverse_node_dict:
                    output_list.append("reticulation")
        parent_type_dict[i] = output_list

    # Children
    for i, child in enumerate(graph.successors(node)):
        output_list = []
        if z_in_tree:
            if signature.embedding.node_dict[child] == child:
                child_type_dict[i] = ["leaf"]
                continue
            if graph.in_degree(child) <= 1:
                output_list.append("tree")
            if graph.out_degree(child) <= 0:
                output_list.append("leaf")
        else:
            if graph.in_degree(child) <= 1:
                output_list.append("tree")
            if child in signature.embedding.inverse_node_dict:
                if signature.embedding.inverse_node_dict[child] == child:
                    child_type_dict[i] = ["leaf"]
                    continue
                if graph.out_degree(child) <= 0:
                    output_list.append("leaf")
            else:
                if graph.out_degree(child) <= 1:
                    output_list.append("reticulation")
        child_type_dict[i] = output_list

    return parent_type_dict, child_type_dict


def neighbor_definite_type_check(graph, node):
    """This function checks the types of the neighbors of a node"""
    parent_type_dict = {}
    child_type_dict = {}
    # Check types of neighbors in the input network
    for i, parent in enumerate(graph.predecessors(node)):
        if graph.in_degree(parent) == 0:
            parent_type_dict[i] = "root"
        elif graph.out_degree(parent) == 0:
            parent_type_dict[i] = "leaf"
        elif graph.in_degree(parent) == 2:
            parent_type_dict[i] = "reticulation"
        else:
            parent_type_dict[i] = "tree"

    for i, child in enumerate(graph.successors(node)):
        if graph.in_degree(child) == 0:
            child_type_dict[i] = "root"
        elif graph.out_degree(child) == 0:
            child_type_dict[i] = "leaf"
        elif graph.in_degree(child) == 2:
            child_type_dict[i] = "reticulation"
        else:
            child_type_dict[i] = "tree"

    return parent_type_dict, child_type_dict


def introduce_node(tree_in, network_in, signature, node_z, z_in_tree, descendant_in_dict, depth_in_dict, neighbor_in_dict, sibling_in_dict, super_compact):
    possible_candidates = []
    output_list = []

    if z_in_tree:
        graph_in = tree_in
        graph_used = signature.tree
    else:
        graph_in = network_in
        graph_used = signature.network

    type_z = definite_type_check(graph_in, node_z)
    if type_z == "leaf":
        return introduce_leaf(tree_in, network_in, signature, node_z, z_in_tree, descendant_in_dict, depth_in_dict, super_compact)

    # [[parent1], [parent2], [child1], [child2]]
    present_list = [[], [], [], []]

    # print(f"node_z = {node_z}")

    # Check for present parents
    for count, theoretical_parent in enumerate(graph_in.predecessors(node_z)):
        if theoretical_parent in signature.inverse_iso_labelling:  # If the theoretical_parent is present:
            actual_parent = signature.inverse_iso_labelling[theoretical_parent]
            # print(f"actual_parent present {theoretical_parent} = {actual_parent}")

            # Add any child of the parent with the "FUTURE" label to the possible candidates
            for successor in graph_used.successors(actual_parent):
                if signature.iso_labelling[successor] == "FUTURE":
                    present_list[count].append(successor)
                    # print(f"Candidate from parents: {successor}")

            # Try checking if there's any compacted nodes possible:
            if not z_in_tree:
                if type_z not in ["root", "leaf"]:
                    for edge in signature.network.out_edges(actual_parent):
                        label1 = signature.iso_labelling[edge[0]]  # TODO: This one is not needed, right?
                        label2 = signature.iso_labelling[edge[1]]
                        # Don't mess with PAST arcs
                        if label1 == "PAST":
                            continue
                        if label2 == "PAST":
                            continue
                        # Don't decompact edges that are not embedding arcs.
                        if edge not in signature.embedding.inverse_edge_dict:
                            continue
                        # Don't decompact edges that are in the input graph
                        if network_in.has_edge(label1, label2):
                            continue
                        present_list[count].append(edge)
                        # print(f"Compact edge to parents: {edge}")

            # If the actual_parent was there but we found no possible options:
            if not present_list[count]:
                return []

    # Check for present children
    for count, theoretical_child in enumerate(graph_in.successors(node_z)):
        if theoretical_child in signature.inverse_iso_labelling:  # If the theoretical_child is present:
            actual_child = signature.inverse_iso_labelling[theoretical_child]
            # print(f"actual_child present {theoretical_child} = {actual_child}")

            # Add any parent of the child with the "FUTURE" label to the possible candidates
            for predecessor in graph_used.predecessors(actual_child):
                if signature.iso_labelling[predecessor] == "FUTURE":
                    present_list[count + 2].append(predecessor)
                    # print(f"Candidate from children: {predecessor}")

            # Try checking if there's any compacted nodes possible:
            if not z_in_tree:
                if type_z not in ["root", "leaf"]:
                    for edge in signature.network.in_edges(actual_child):
                        label1 = signature.iso_labelling[edge[0]]
                        label2 = signature.iso_labelling[edge[1]]
                        # Don't mess with PAST arcs
                        if label1 == "PAST":
                            continue
                        if label2 == "PAST":
                            continue
                        # Don't decompact edges that are in the input graph
                        if network_in.has_edge(label1, label2):
                            continue
                        # Don't decompact edges that are not embedding arcs.
                        if edge not in signature.embedding.inverse_edge_dict:
                            continue
                        present_list[count + 2].append(edge)
                        # print(f"Compact edge to children: {edge}")

            # If the actual_child was there but we found no possible FUTURE options:
            if not present_list[count + 2]:
                return []

    # print(f"present_list = {present_list}")

    # Check which candidates are good (by checking which are adjacent to ALL present nodes)
    first_non_empty = True
    for candidate_list in present_list:
        if not candidate_list:  # If candidate_list is empty
            continue
        else:
            if first_non_empty:
                first_non_empty = False
                possible_candidates = candidate_list
            else:
                # Take the intersection of old candidates with new candidates
                possible_candidates = [candidate for candidate in possible_candidates if candidate in candidate_list]

    # Sort candidates on tuple / node:
    possible_compacted = [candidate for candidate in possible_candidates if type(candidate) == tuple]
    possible_normals = [candidate for candidate in possible_candidates if type(candidate) != tuple]

    # Checking for correct node types
    possible_candidates = []
    for candidate in possible_normals:
        if graph_used.in_degree(candidate) <= graph_in.in_degree(node_z):
            if graph_used.out_degree(candidate) <= graph_in.out_degree(node_z):
                # Don't use nodes that are a leaf in the signature but not in the input graph (other way around is fine)
                if graph_in.out_degree(node_z) != 0 and candidate in signature.network and candidate in signature.tree:
                    continue
                # Don't use nodes with an embedding for reticulation nodes
                if type_z == "reticulation" and candidate in signature.embedding.inverse_node_dict:
                    continue
                # We don't check leaf nodes explicitly, since those can change on the fly
                possible_candidates.append(candidate)

    # If there are no candidates:
    if first_non_empty:  # This remains True if no list had items
        # print("No restrictions!")  # If there's no nodes with any present neighbors, there's just no neighbors. TODO, check this if something goes wrong.

        # Add a signature with a new node
        new_signature = signature.signature_copy()
        new_node = new_signature.node_count + 1
        new_signature.node_count += 1
        new_signature.iso_label(new_node, node_z)

        # 1. If z is a leaf:
        if type_z == "leaf":
            new_signature.tree.add_node(new_node)  # If z is a leaf, only add 1 node (to both the tree and network)
            new_signature.network.add_node(new_node)

            new_signature.embedding.node_dict[new_node] = new_node
            new_signature.embedding.inverse_node_dict[new_node] = new_node

        # 2. If z is in the network
        elif node_z in network_in:

            # 2.1: Pass a signature without embedded tree node
            # Don't pass a non-embedding node if z is a root (Edgecase 3)
            new_signature.network.add_node(new_node)  # TODO: order changed
            if type_z != "root":
                output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

            # 2.2: Pass a signature with embedded tree node
            new_signature = new_signature.signature_copy()
            tree_node = new_signature.node_count + 1
            new_signature.node_count += 1
            new_signature.tree.add_node(tree_node)
            new_signature.iso_label(tree_node, "FUTURE")

            new_signature.embedding.node_dict[tree_node] = new_node
            new_signature.embedding.inverse_node_dict[new_node] = tree_node

        # 3. If z is in the tree
        else:
            new_signature.tree.add_node(new_node)
            network_node = new_signature.node_count + 1
            new_signature.node_count += 1
            new_signature.network.add_node(network_node)

            new_signature.embedding.node_dict[new_node] = network_node
            new_signature.embedding.inverse_node_dict[network_node] = new_node

            new_signature.iso_label(new_node, node_z)
            new_signature.iso_label(network_node, "FUTURE")

        output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

        # Find existing nodes that could be the one and make sure the types are the same
        for node in graph_used:
            if new_signature.iso_labelling[node] == "FUTURE":
                if graph_used.in_degree(node) <= graph_in.in_degree(node_z):
                    if graph_used.out_degree(node) <= graph_in.out_degree(node_z):
                        # Check if either both are leaves or both are not leaves using NOT XOR (where XOR = ^)
                        if node in new_signature.embedding.node_dict:
                            if (new_signature.embedding.node_dict[node] == node) ^ (graph_in.out_degree(node_z) == 0):
                                # print("XOR", node)
                                continue
                        # Check if node has enough spots left for leaf children: TODO: this currently uses a soft leaf definition for present stuff, since they can be changed into leaves later.
                        present_leaves = 0
                        needed_leaves = 0
                        for child in graph_in.successors(node_z):
                            if graph_in.out_degree(child) == 0:
                                needed_leaves += 1
                        for child in graph_used.successors(node):
                            if graph_used.out_degree(child) == 0:
                                present_leaves += 1
                        if graph_in.out_degree(node_z) - graph_used.out_degree(node) + present_leaves >= needed_leaves:
                            possible_candidates.append(node)
                            # print(f"Possible node: {node}")

                        # TODO: could check here for root nodes?

        # Find existing edges that can be de-compacted
        if not z_in_tree:
            if type_z == "tree" or type_z == "reticulation":
                for edge in graph_used.edges():
                    # Don't mess with PAST arcs
                    if signature.iso_labelling[edge[0]] == "PAST":
                        continue
                    if signature.iso_labelling[edge[1]] == "PAST":
                        continue
                    # Don't decompact edges that are not embedding arcs.
                    if edge not in signature.embedding.inverse_edge_dict:
                        continue
                    possible_compacted.append(edge)

        if not super_compact:
            # Regular compactness only
            # Check if candidates are not adjacent to nodes they should not be adjacent to
            z_neighbors = set(itertools.chain(graph_in.successors(node_z), graph_in.predecessors(node_z)))

            temp_remove_list = []
            for candidate in possible_candidates:
                for neighbor in itertools.chain(graph_used.successors(candidate), graph_used.predecessors(candidate)):
                    if signature.iso_labelling[neighbor] == "FUTURE":
                        continue
                    if signature.iso_labelling[neighbor] == "PAST":
                        continue
                    if signature.iso_labelling[neighbor] not in z_neighbors:
                        temp_remove_list.append(candidate)
                        break
                # Don't pass a non-embedding node if z is a root (Edgecase 3)
                if type_z == "root":
                    if candidate not in signature.embedding.inverse_node_dict and candidate not in signature.embedding.node_dict:
                        temp_remove_list.append(candidate)

            for candidate in temp_remove_list:
                possible_candidates.remove(candidate)

    # print(f"possible_candidates = {possible_candidates}")
    # print(f"possible_compacted = {possible_compacted}")

    # Change isolabelling and pass multiple options
    for node in possible_candidates:
        new_signature = signature.signature_copy()
        new_signature.iso_label(node, node_z)

        output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

    for compact_edge in possible_compacted:
        # De-compact edge
        # print("De-Compacting")
        new_signature = signature.signature_copy()

        new_node = new_signature.decompact(compact_edge)
        new_signature.iso_label(new_node, node_z)
        output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

    if len(output_list) > 0:
        # print("\nCHECKING")
        # print(f"Before: {len(output_list)} signatures")
        output_list = [check_signature for check_signature in output_list if
                       (TreeContainmentChecks.descendant_check(check_signature, descendant_in_dict, depth_in_dict) and
                        TreeContainmentChecks.neighbor_check(check_signature, neighbor_in_dict) and
                        TreeContainmentChecks.correctness_check(check_signature) and
                        TreeContainmentChecks.quantity_check(check_signature, network_in, tree_in) and
                        TreeContainmentChecks.sibling_check(check_signature, sibling_in_dict)
                        )]
        # print(f"After: {len(output_list)} signatures")

    return output_list


def introduce_leaf(tree_in, network_in, signature, node_z, z_in_tree, descendant_in_dict, depth_in_dict, super_compact):
    output_list = []

    present_network_parents = []
    present_tree_parents = []

    # print(f"node_z = {node_z}")

    # Check for present network parent
    for theoretical_parent in network_in.predecessors(node_z):
        if theoretical_parent in signature.inverse_iso_labelling:  # If the theoretical_parent is present:
            actual_parent = signature.inverse_iso_labelling[theoretical_parent]
            # print(f"network_parent present {theoretical_parent} = {actual_parent}")

            # Add any child of the parent with the "FUTURE" label to the possible candidates
            for successor in signature.network.successors(actual_parent):
                if signature.iso_labelling[successor] == "FUTURE":
                    present_network_parents.append(successor)
                    # print(f"Candidate from parents: {successor}")

            # If the actual_parent was there but we found no possible options:
            if not present_network_parents:
                return []

    # Check for present tree parent
    for theoretical_parent in tree_in.predecessors(node_z):
        if theoretical_parent in signature.inverse_iso_labelling:  # If the theoretical_parent is present:
            actual_parent = signature.inverse_iso_labelling[theoretical_parent]
            # print(f"tree_parent present {theoretical_parent} = {actual_parent}")

            # Add any child of the parent with the "FUTURE" label to the possible candidates
            for successor in signature.tree.successors(actual_parent):
                if signature.iso_labelling[successor] == "FUTURE":
                    present_tree_parents.append(successor)
                    # print(f"Candidate from parents: {successor}")

            # If the actual_parent was there but we found no possible options:
            if not present_tree_parents:
                return []

    # print(f"present_network_parents = {present_network_parents}")
    # print(f"present_tree_parents = {present_tree_parents}")

    candidate_list = []
    on_the_fly_list = []
    no_restrictions = False

    if present_tree_parents:
        # If there's nodes in both
        if present_network_parents:
            for node in present_tree_parents:
                # Normal leaf
                if node in present_network_parents:
                    candidate_list.append(node)
                # On the fly change needed
                elif signature.embedding.node_dict[node] in present_network_parents:
                    on_the_fly_list.append(node)

        # If there's just nodes in present_tree_parents
        else:
            for node in present_tree_parents:
                # Normal leaf
                if signature.embedding.node_dict[node] == node:
                    candidate_list.append(node)
                else:
                    on_the_fly_list.append(node)

    else:
        # If there's just nodes in present_network_parents
        if present_network_parents:
            for node in present_network_parents:
                if node in signature.embedding.inverse_node_dict:
                    # Normal leaf
                    if signature.embedding.inverse_node_dict[node] == node:
                        candidate_list.append(node)
                    else:
                        on_the_fly_list.append(node)

        # If there's nodes in neither
        else:
            no_restrictions = True

    # Checking for correct node types for on the fly (assuming normal leaves are fine)
    # print(f"on_the_fly_list = {on_the_fly_list}")
    filtered_on_the_fly = [[], [], []]
    for node in on_the_fly_list:
        # Tree node:
        if node in signature.tree:
            if (signature.tree.in_degree(node) == 1 and
               signature.tree.out_degree(node) == 0 and
               signature.network.in_degree(signature.embedding.node_dict[node]) == 1 and
               signature.network.out_degree(signature.embedding.node_dict[node]) == 0):
                filtered_on_the_fly[0].append(node)

        # Network node:
        else:
            if signature.network.in_degree(node) == 1 and signature.network.out_degree(node) == 0:
                if node in signature.embedding.inverse_node_dict:
                    inverse_node = signature.embedding.inverse_node_dict[node]
                    if signature.tree.in_degree(inverse_node) == 1 and signature.tree.out_degree(inverse_node) == 0:
                        filtered_on_the_fly[1].append(node)
                else:
                    filtered_on_the_fly[2].append(node)

    # If there are no candidates:
    if no_restrictions:  # This remains True if no list had items
        # print("No restrictions!")  # If there's no nodes with any present neighbors, there's just no neighbors. TODO, check this if something goes wrong.

        # Add a signature with a new node
        new_signature = signature.signature_copy()
        new_node = new_signature.node_count + 1
        new_signature.node_count += 1
        new_signature.iso_label(new_node, node_z)

        new_signature.tree.add_node(new_node)
        new_signature.network.add_node(new_node)

        new_signature.embedding.node_dict[new_node] = new_node
        new_signature.embedding.inverse_node_dict[new_node] = new_node

        output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

        # Find existing nodes that could be the one and make sure the types are the same
        for node in signature.tree.nodes():
            if signature.iso_labelling[node] == "FUTURE":
                if signature.embedding.node_dict[node] == node:
                    candidate_list.append(node)
                    # print(f"Possible node: {node}")

                else:
                    if signature.tree.in_degree(node) == 1 and signature.tree.out_degree(node) == 0:
                        embedded_node = signature.embedding.node_dict[node]
                        if (signature.network.in_degree(embedded_node) == 1 and
                                signature.network.out_degree(embedded_node) == 0):
                            filtered_on_the_fly[0].append(node)
                            # print(f"Possible on the fly: {node}")

    # print(f"candidate_list = {candidate_list}")
    # print(f"on_the_fly_list = {on_the_fly_list}")
    # print(f"filtered_on_the_fly = {filtered_on_the_fly}")

    # Change isolabelling and pass multiple options
    for node in candidate_list:
        new_signature = signature.signature_copy()
        new_signature.iso_label(node, node_z)
        output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

    # Change node type into leaf "on the fly"
    # Tree nodes with embedding
    for node in filtered_on_the_fly[0]:
        # print("Changing stuff on the fly")
        new_signature = signature.signature_copy()
        new_signature.iso_label(node, node_z)
        embedding_node = new_signature.embedding.node_dict[node]
        # Remove the network node and attach its parent to the changed leaf
        for network_parent in new_signature.network.predecessors(embedding_node):  # There is only 1 parent
            for tree_parent in new_signature.tree.predecessors(node):  # There is only 1 parent
                # Remove network node
                new_signature.network.remove_node(embedding_node)
                new_signature.iso_labelling.pop(embedding_node)
                new_signature.embedding.inverse_node_dict.pop(embedding_node)

                new_signature.network.add_edge(network_parent, node)
                embedding_path = new_signature.embedding.edge_dict[(tree_parent, node)]
                removed_edge = embedding_path.pop()  # Remove last item
                new_signature.embedding.inverse_edge_dict.pop(removed_edge)
                embedding_path.append((network_parent, node))
                new_signature.embedding.edge_dict[(tree_parent, node)] = embedding_path
                new_signature.embedding.inverse_edge_dict[(network_parent, node)] = (tree_parent, node)
                new_signature.embedding.node_dict[node] = node
                new_signature.embedding.inverse_node_dict[node] = node
                # new_signature.print()
        output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

    # Network nodes with embedded
    for node in filtered_on_the_fly[1]:
        node = signature.embedding.inverse_node_dict[node]
        new_signature = signature.signature_copy()
        new_signature.iso_label(node, node_z)
        embedding_node = new_signature.embedding.node_dict[node]
        # Remove the network node and attach its parent to the changed leaf
        for network_parent in new_signature.network.predecessors(embedding_node):  # There is only 1 parent
            for tree_parent in new_signature.tree.predecessors(node):  # There is only 1 parent
                # Remove network node
                new_signature.network.remove_node(embedding_node)
                new_signature.iso_labelling.pop(embedding_node)
                new_signature.embedding.inverse_node_dict.pop(embedding_node)

                new_signature.network.add_edge(network_parent, node)
                embedding_path = new_signature.embedding.edge_dict[(tree_parent, node)]
                removed_edge = embedding_path.pop()  # Remove last item
                new_signature.embedding.inverse_edge_dict.pop(removed_edge)
                embedding_path.append((network_parent, node))
                new_signature.embedding.edge_dict[(tree_parent, node)] = embedding_path
                new_signature.embedding.inverse_edge_dict[(network_parent, node)] = (tree_parent, node)
                new_signature.embedding.node_dict[node] = node
                new_signature.embedding.inverse_node_dict[node] = node
                # new_signature.print()
        output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

    # Network nodes without inverse embedding
    for node in filtered_on_the_fly[2]:
        node = signature.embedding.inverse_node_dict[node]
        new_signature = signature.signature_copy()
        new_signature.iso_label(node, node_z)
        embedding_node = new_signature.embedding.node_dict[node]
        # Remove the network node and attach its parent to the changed leaf
        for network_parent in new_signature.network.predecessors(embedding_node):  # There is only 1 parent
            for tree_parent in new_signature.tree.predecessors(node):  # There is only 1 parent
                # Remove network node
                new_signature.network.remove_node(embedding_node)
                new_signature.iso_labelling.pop(embedding_node)
                new_signature.embedding.inverse_node_dict.pop(embedding_node)

                new_signature.network.add_edge(network_parent, node)
                embedding_path = new_signature.embedding.edge_dict[(tree_parent, node)]
                removed_edge = embedding_path.pop()  # Remove last item
                new_signature.embedding.inverse_edge_dict.pop(removed_edge)
                embedding_path.append((network_parent, node))
                new_signature.embedding.edge_dict[(tree_parent, node)] = embedding_path
                new_signature.embedding.inverse_edge_dict[(network_parent, node)] = (tree_parent, node)
                new_signature.embedding.node_dict[node] = node
                new_signature.embedding.inverse_node_dict[node] = node
                # new_signature.print()
        output_list.extend(introduce_constructor(tree_in, network_in, new_signature, node_z, z_in_tree, super_compact))

    if output_list:
        # print("\nCHECKING")
        # print(f"Before: {len(output_list)} signatures")
        output_list = [check_signature for check_signature in output_list if
                       (TreeContainmentChecks.descendant_check(check_signature, descendant_in_dict, depth_in_dict) and
                        TreeContainmentChecks.correctness_check(check_signature) and
                        TreeContainmentChecks.quantity_check(check_signature, network_in, tree_in)
                        )]

        # output_list = [check_signature for check_signature in output_list if TreeContainmentChecks.descendant_check(check_signature, descendant_in_dict, depth_in_dict)]
        # print(f"After: {len(output_list)} signatures")

    return output_list


def introduce_constructor(tree_in, network_in, signature, node_z, z_in_tree, super_compact):
    # print("   introduce_constructor")

    new_node = signature.inverse_iso_labelling[node_z]

    output_list = []
    parent_list = [[], []]
    child_list = [[], []]

    # Tree node:
    if z_in_tree:
        part_of_embedding = True
        graph_in = tree_in
        graph_used = signature.tree

        # Add an embedding node if z does not yet have one
        if new_node not in signature.embedding.node_dict:
            embedding_node = signature.node_count
            signature.node_count += 1
            signature.embedding.node_dict[new_node] = embedding_node
            signature.embedding.inverse_node_dict[embedding_node] = new_node

        else:
            embedding_node = signature.embedding.node_dict[new_node]

    # Network node:
    else:
        graph_in = network_in
        graph_used = signature.network

        # Check if part of the embedding
        part_of_embedding = new_node in signature.embedding.inverse_node_dict

        if part_of_embedding:
            embedding_node = signature.embedding.inverse_node_dict[new_node]  # TODO: different name?
        else:
            embedding_node = None
    # print(f"   Node: {node_z} = {new_node}")

    # Set up list of neighbors
    neighbors = [new_node]
    for parent in graph_used.predecessors(new_node):
        neighbors.append(parent)
    for child in graph_used.successors(new_node):
        neighbors.append(child)

    parent_type_dict, child_type_dict = neighbor_definite_type_check(graph_in, node_z)
    current_parent_dict, current_child_dict = neighbor_possible_type_check(signature, graph_used, new_node, z_in_tree)

    # If it has 2 leaves as children, it MUST be part of the embedding. So if it's not, kill it
    if not part_of_embedding:
        if 1 in child_type_dict:  # Check if there's even 2 children
            if child_type_dict[0] == "leaf" and child_type_dict[1] == "leaf":
                return []

    # Dictionaries that contain the required types of nodes
    # print(f"   parent_type_dict = {parent_type_dict}")
    # print(f"   child_type_dict = {child_type_dict}")

    # Dictionaries that contain the current types of nodes
    # print(f"   current_parent_dict = {current_parent_dict}")
    # print(f"   current_child_dict = {current_child_dict}")

    # TODO: Check if this part can be pruned a bit
    # Check which parents are needed
    if graph_in.in_degree(node_z) > graph_used.in_degree(new_node):
        # Filter parent types to remove unnecessary types
        for current_number in current_parent_dict:
            current_parent_dict[current_number] = [parent_type for parent_type in current_parent_dict[current_number] if parent_type in parent_type_dict.values()]

        original_current_parent_dict = current_parent_dict.copy()

        already_used = False
        for count, parent_number in enumerate(parent_type_dict):
            for present_type in current_parent_dict:  # Should be only 1
                # Check if present_node contains the required type
                if parent_type_dict[parent_number] in current_parent_dict[present_type]:
                    # Remove the used type from the present_node
                    current_parent_dict[present_type].remove(parent_type_dict[parent_number])
                    if already_used:
                        parent_list[1] = original_current_parent_dict[present_type]
                    else:
                        # If empty, make it None
                        if not parent_list[count]:
                            parent_list[count].append(None)
                        already_used = True
            if not parent_list[count]:  # If empty
                parent_list[count] = ["new"]

    # Check which children are needed
    if graph_in.out_degree(node_z) > graph_used.out_degree(new_node):
        original_current_child_dict = current_child_dict.copy()
        already_used = False
        for count, required_node in enumerate(child_type_dict):
            for present_node in current_child_dict:
                # Check if a present node contains the required type
                if child_type_dict[required_node] in current_child_dict[present_node]:
                    # Remove the used type from the present_node
                    current_child_dict[present_node].remove(child_type_dict[required_node])
                    # print(f"   already_used = {already_used}")
                    # Check if the node is already used (1 node since 2 > graph_in_out_degree > graph_used.out_degree)
                    if already_used:
                        # print(f"required_node = {required_node}")

                        # print(f"original_current_child_dict = {original_current_child_dict}")

                        # print(original_current_child_dict)
                        child_list[1] = original_current_child_dict[0]  # TODO: This is where it crashes
                        # child_list[1] = original_current_child_dict[required_node]  # TODO: This is where it crashes

                    else:
                        if not child_list[count]:
                            child_list[count].append(None)
                        already_used = True
            if not child_list[count]:  # If empty
                child_list[count] = ["new"]

    # print(f"   parent_list = {parent_list}")
    # print(f"   child_list = {child_list}")

    # Check if the number of incoming/outgoing edges needed + existing incoming/outgoing edges is too large (edgecase 6)
    number_of_in_edges = graph_used.in_degree(new_node)
    if not (parent_list[0] == [None] or parent_list[0] == []):
        number_of_in_edges += 1
    if not (parent_list[1] == [None] or parent_list[1] == []):
        number_of_in_edges += 1
    if number_of_in_edges > len(parent_type_dict):
        # print("Ignored requirement, due to too many parents (edgecase 6)")
        parent_list[1] = []

    number_of_out_edges = graph_used.out_degree(new_node)
    if not (child_list[0] == [None] or child_list[0] == []):
        number_of_out_edges += 1
    if not (child_list[1] == [None] or child_list[1] == []):
        number_of_out_edges += 1
    if number_of_out_edges > len(child_type_dict):
        # print("Ignored requirement, due to too many children (edgecase 6)")  # TODO: test this!
        child_list[1] = []

    # Find nodes within display graph that can satisfy these needs
    # Parents
    for i, sublist in enumerate(parent_list):
        if sublist == ['new']:
            needed_type = parent_type_dict[i]
            # print(f"   needed_type parent = {needed_type}")
            if needed_type == "tree" or needed_type == "reticulation":
                for node in graph_used.nodes():
                    # Only use FUTURE nodes
                    if signature.iso_labelling[node] != "FUTURE":
                        continue
                    # Don't use leaves
                    if node in signature.tree and node in signature.network:
                        continue
                    # If node_z is not an embedding yet already has embedding edge, don't use embeddings as new neighbors (edgecase 8) # TODO: test this TODO: why is this done only when there's 1 parent? Shouldn't it also be when there's 1 child?
                    if not part_of_embedding:
                        if node in signature.embedding.inverse_node_dict:
                            temp_parents = list(graph_used.predecessors(new_node))
                            if len(temp_parents) == 1:
                                if (temp_parents[0], new_node) in signature.embedding.inverse_edge_dict:
                                    continue
                    # Check whether node is still able to become the required type
                    if node in neighbors:
                        continue
                    # Dont use nodes without space
                    if graph_used.in_degree(node) + graph_used.out_degree(node) > 2:
                        continue
                    parent_list[i].append(node)

                # Try compacted edges when adding a non-embedded node:
                if not part_of_embedding:
                    # for edge in signature.compact_edges:
                    for edge in signature.network.edges():
                        label1 = signature.iso_labelling[edge[0]]
                        label2 = signature.iso_labelling[edge[1]]
                        # Don't mess with PAST arcs
                        if label1 == "PAST":
                            continue
                        if label2 == "PAST":
                            continue
                        # Don't decompact non-embedding edges
                        if edge not in signature.embedding.inverse_edge_dict:
                            continue
                        # Don't decompact edges that are in the input graph
                        if network_in.has_edge(label1, label2):
                            continue
                        # Check if other end of compacted edge is not the new_node
                        if new_node in edge:
                            continue
                        parent_list[i].append(edge)

    # Children
    for i, sublist in enumerate(child_list):
        if sublist == ['new']:
            needed_type = child_type_dict[i]
            # print(f"   needed_type child = {needed_type}")
            if needed_type == "tree" or needed_type == "reticulation":
                for node in graph_used.nodes():
                    # Only use FUTURE nodes
                    if signature.iso_labelling[node] != "FUTURE":
                        continue
                    # Don't use leaves
                    if node in signature.tree and node in signature.network:
                        continue
                    # If node_z is an embedding, don't use embeddings with in_degree 1 (edgecase 7)
                    if node in signature.embedding.inverse_node_dict and graph_used.in_degree(node) == 1:
                        continue
                    # If node_z is not an embedding yet already has embedding edge, don't use embeddings as new neighbors (edgecase 8) # TODO: test this
                    if not part_of_embedding:
                        if node in signature.embedding.inverse_node_dict:
                            temp_children = list(graph_used.successors(new_node))
                            if len(temp_children) == 1:
                                if (new_node, temp_children[0]) in signature.embedding.inverse_edge_dict:
                                    continue
                    # Check whether node is still able to become the required type
                    if node in neighbors:
                        continue
                    if graph_used.in_degree(node) + graph_used.out_degree(node) > 2:
                        continue
                    child_list[i].append(node)

                # Try compacted edges when adding a non-embedded node:
                if not part_of_embedding:
                    # for edge in signature.compact_edges:
                    for edge in signature.network.edges():
                        label1 = signature.iso_labelling[edge[0]]
                        label2 = signature.iso_labelling[edge[1]]
                        # Don't mess with PAST arcs
                        if label1 == "PAST":
                            continue
                        if label2 == "PAST":
                            continue
                        # Don't decompact non-embedding edges
                        if edge not in signature.embedding.inverse_edge_dict:
                            continue
                        # Don't decompact edges that are in the input graph
                        if network_in.has_edge(label1, label2):
                            continue
                        # Check if other end of compacted edge is not the new_node
                        if new_node in edge:
                            continue
                        child_list[i].append(edge)

    # Add None to empty lists (to make the next section work)
    for sublist in parent_list:
        if not sublist:  # Check if it is empty
            sublist.append(None)
    for sublist in child_list:
        if not sublist:
            sublist.append(None)

    # print("   After search:")
    # print(f"   parent_list = {parent_list}")
    # print(f"   child_list = {child_list}")
    # print()
    # print(f"      Part of the embedding: {part_of_embedding}")
    # print(f"      Z is in the tree: {z_in_tree}")

    # List of non-embedded nodes that have space for edges
    extra_node_list = [node for node in signature.network.nodes()
                       if node not in signature.embedding.inverse_node_dict
                       and signature.network.in_degree(node) + signature.network.out_degree(node) <= 1
                       and node != new_node]
    # print(f"      extra_node_list = {extra_node_list}")

    for a in parent_list[0]:

        for b in parent_list[1]:
            if type(b) == int and b == a:
                continue

            for c in child_list[0]:
                if type(c) == int and (c == a or c == b):
                    continue

                for d in child_list[1]:
                    if type(d) == int and (d == a or d == b or d == c):
                        continue

                    # print(f"      [a, b, c, d] = {[a, b, c, d]}")

                    new_signature = signature.signature_copy()
                    a_new = None
                    b_new = None
                    c_new = None
                    d_new = None

                    # Path lists for inserting nodes in between and other stuff
                    #
                    path_list_a = []
                    path_list_b = []
                    path_list_c = []
                    path_list_d = []

                    # PART OF THE EMBEDDING
                    if part_of_embedding:

                        # TREE
                        if z_in_tree:

                            # A
                            if type(a) == int:
                                a_new = a  # Useful for later during possible path construction
                                new_signature.tree.add_edge(a, new_node)
                                # Add (embedding_path, new_edge)
                                path_list_a.append(([(new_signature.embedding.node_dict[a], embedding_node)],
                                                    [(new_signature.embedding.node_dict[a], embedding_node)]))

                            elif a == "new":
                                a_new = new_signature.node_count + 1
                                new_signature.node_count += 1
                                new_signature.tree.add_edge(a_new, new_node)
                                new_signature.iso_labelling[a_new] = "FUTURE"

                                a_embedded = new_signature.node_count + 1
                                new_signature.node_count += 1
                                new_signature.iso_labelling[a_embedded] = "FUTURE"
                                new_signature.embedding.node_dict[a_new] = a_embedded
                                new_signature.embedding.inverse_node_dict[a_embedded] = a_new

                                path_list_a.append(([(a_embedded, embedding_node)],
                                                    [(a_embedded, embedding_node)]))

                            # Adding extra nodes in between the paths
                            if a is not None:
                                if extra_node_list:
                                    new_path_list_a = path_list_a.copy()
                                    for existing_path in path_list_a:
                                        for i in range(len(extra_node_list)):
                                            j = i + 1
                                            for permutation_tuple in itertools.permutations(extra_node_list, j):
                                                for permutation_element in permutation_tuple:
                                                    # Insert permutation elements in between existing edges
                                                    for count, edge in enumerate(existing_path[0]):
                                                        altered_existing_path = [e for e in existing_path[0] if e != edge]
                                                        altered_existing_edges = [e for e in existing_path[1] if e != edge]

                                                        altered_existing_path.insert(count, (edge[0], permutation_element))
                                                        altered_existing_path.insert(count+1, (permutation_element, edge[1]))
                                                        altered_existing_edges.append((edge[0], permutation_element))
                                                        altered_existing_edges.append((permutation_element, edge[1]))

                                                        new_path_list_a.append((altered_existing_path, altered_existing_edges, tuple(permutation_tuple)))

                                    path_list_a = new_path_list_a

                                # Non-super-compact paths:
                                if not super_compact:
                                    compact_path_list = []
                                    for existing_path in path_list_a:
                                        # Copy the path
                                        if len(existing_path) == 2:
                                            copy_path = (existing_path[0][:], existing_path[1][:])
                                        else:
                                            copy_path = (existing_path[0][:], existing_path[1][:], existing_path[2][:])

                                        # Add another node in between the path
                                        inbetween_edge = copy_path[0].pop()
                                        copy_path[0].append((inbetween_edge[0], new_signature.node_count+10))
                                        copy_path[0].append((new_signature.node_count+10, inbetween_edge[1]))
                                        inbetween_edge = copy_path[1].pop()
                                        copy_path[1].append((inbetween_edge[0], new_signature.node_count+10))
                                        copy_path[1].append((new_signature.node_count+10, inbetween_edge[1]))
                                        compact_path_list.append(copy_path)
                                    path_list_a.extend(compact_path_list)

                            # B
                            if type(b) == int:
                                b_new = b  # Useful for later during possible path construction
                                new_signature.tree.add_edge(b, new_node)
                                # Add (embedding_path, new_edge)
                                path_list_b.append(([(new_signature.embedding.node_dict[b], embedding_node)],
                                                    [(new_signature.embedding.node_dict[b], embedding_node)]))

                            elif b == "new":
                                b_new = new_signature.node_count + 1
                                new_signature.node_count += 1
                                new_signature.tree.add_edge(b_new, new_node)
                                new_signature.iso_labelling[b_new] = "FUTURE"

                                b_embedded = new_signature.node_count + 1
                                new_signature.node_count += 1
                                new_signature.iso_labelling[b_embedded] = "FUTURE"
                                new_signature.embedding.node_dict[b_new] = b_embedded
                                new_signature.embedding.inverse_node_dict[b_embedded] = b_new

                                path_list_b.append(([(b_embedded, embedding_node)],
                                                    [(b_embedded, embedding_node)]))

                            # Adding extra nodes in between the paths
                            if b is not None:
                                if extra_node_list:
                                    new_path_list_b = path_list_b.copy()
                                    for existing_path in path_list_b:
                                        for i in range(len(extra_node_list)):
                                            j = i + 1
                                            for permutation_tuple in itertools.permutations(extra_node_list, j):
                                                for permutation_element in permutation_tuple:
                                                    # Insert permutation elements in between existing edges
                                                    for count, edge in enumerate(existing_path[0]):
                                                        altered_existing_path = [e for e in existing_path[0] if e != edge]
                                                        altered_existing_edges = [e for e in existing_path[1] if e != edge]

                                                        altered_existing_path.insert(count, (edge[0], permutation_element))
                                                        altered_existing_path.insert(count+1, (permutation_element, edge[1]))
                                                        altered_existing_edges.append((edge[0], permutation_element))
                                                        altered_existing_edges.append((permutation_element, edge[1]))

                                                        new_path_list_b.append((altered_existing_path, altered_existing_edges, tuple(permutation_tuple)))

                                    path_list_b = new_path_list_b

                                # Non-super-compact paths:
                                if not super_compact:
                                    compact_path_list = []
                                    for existing_path in path_list_b:
                                        # Copy the path
                                        if len(existing_path) == 2:
                                            copy_path = (existing_path[0][:], existing_path[1][:])
                                        else:
                                            copy_path = (existing_path[0][:], existing_path[1][:], existing_path[2][:])

                                        # Add another node in between the path
                                        inbetween_edge = copy_path[0].pop()
                                        copy_path[0].append((inbetween_edge[0], new_signature.node_count+11))
                                        copy_path[0].append((new_signature.node_count+11, inbetween_edge[1]))
                                        inbetween_edge = copy_path[1].pop()
                                        copy_path[1].append((inbetween_edge[0], new_signature.node_count+11))
                                        copy_path[1].append((new_signature.node_count+11, inbetween_edge[1]))
                                        compact_path_list.append(copy_path)
                                    path_list_b.extend(compact_path_list)

                            # C
                            if type(c) == int:
                                c_new = c  # Useful for later during possible path construction
                                new_signature.tree.add_edge(new_node, c)
                                # Add (embedding_path, new_edge)
                                path_list_c.append(([(embedding_node, new_signature.embedding.node_dict[c])],
                                                    [(embedding_node, new_signature.embedding.node_dict[c])]))

                            elif c == "new":
                                c_new = new_signature.node_count + 1
                                new_signature.node_count += 1
                                new_signature.tree.add_edge(new_node, c_new)
                                new_signature.iso_labelling[c_new] = "FUTURE"

                                # Option 1: leaf
                                if child_type_dict[0] == "leaf":
                                    new_signature.embedding.node_dict[c_new] = c_new
                                    new_signature.embedding.inverse_node_dict[c_new] = c_new

                                    path_list_c.append(([(embedding_node, c_new)],
                                                        [(embedding_node, c_new)]))

                                # Option 2: non-leaf
                                else:
                                    c_embedded = new_signature.node_count + 1
                                    new_signature.node_count += 1
                                    new_signature.iso_labelling[c_embedded] = "FUTURE"
                                    new_signature.embedding.node_dict[c_new] = c_embedded
                                    new_signature.embedding.inverse_node_dict[c_embedded] = c_new

                                    path_list_c.append(([(embedding_node, c_embedded)],
                                                        [(embedding_node, c_embedded)]))

                            # Adding extra nodes in between the paths
                            if c is not None:
                                if extra_node_list:
                                    new_path_list_c = path_list_c.copy()
                                    for existing_path in path_list_c:
                                        for i in range(len(extra_node_list)):
                                            j = i + 1
                                            for permutation_tuple in itertools.permutations(extra_node_list, j):
                                                for permutation_element in permutation_tuple:
                                                    # Insert permutation elements in between existing edges
                                                    for count, edge in enumerate(existing_path[0]):
                                                        altered_existing_path = [e for e in existing_path[0] if e != edge]
                                                        altered_existing_edges = [e for e in existing_path[1] if e != edge]

                                                        altered_existing_path.insert(count, (edge[0], permutation_element))
                                                        altered_existing_path.insert(count+1, (permutation_element, edge[1]))
                                                        altered_existing_edges.append((edge[0], permutation_element))
                                                        altered_existing_edges.append((permutation_element, edge[1]))

                                                        new_path_list_c.append((altered_existing_path, altered_existing_edges, tuple(permutation_tuple)))

                                    path_list_c = new_path_list_c

                                # Non-super-compact paths:
                                if not super_compact:
                                    compact_path_list = []
                                    for existing_path in path_list_c:
                                        # Copy the path
                                        if len(existing_path) == 2:
                                            copy_path = (existing_path[0][:], existing_path[1][:])
                                        else:
                                            copy_path = (existing_path[0][:], existing_path[1][:], existing_path[2][:])

                                        # Add another node in between the path
                                        inbetween_edge = copy_path[0].pop(0)
                                        copy_path[0].insert(0, (inbetween_edge[0], new_signature.node_count+12))
                                        copy_path[0].insert(1, (new_signature.node_count+12, inbetween_edge[1]))
                                        inbetween_edge = copy_path[1].pop(0)
                                        copy_path[1].insert(0, (inbetween_edge[0], new_signature.node_count+12))
                                        copy_path[1].insert(1, (new_signature.node_count+12, inbetween_edge[1]))

                                        compact_path_list.append(copy_path)
                                    path_list_c.extend(compact_path_list)

                            # D
                            if type(d) == int:
                                d_new = d  # Useful for later during possible path construction
                                new_signature.tree.add_edge(new_node, d)
                                # Add (embedding_path, new_edge)
                                path_list_d.append(([(embedding_node, new_signature.embedding.node_dict[d])],
                                                    [(embedding_node, new_signature.embedding.node_dict[d])]))

                            elif d == "new":
                                d_new = new_signature.node_count + 1
                                new_signature.node_count += 1
                                new_signature.tree.add_edge(new_node, d_new)
                                new_signature.iso_labelling[d_new] = "FUTURE"

                                # Option 1: leaf
                                if child_type_dict[1] == "leaf":
                                    new_signature.embedding.node_dict[d_new] = d_new
                                    new_signature.embedding.inverse_node_dict[d_new] = d_new

                                    path_list_d.append(([(embedding_node, d_new)],
                                                        [(embedding_node, d_new)]))

                                # Option 2: non-leaf
                                else:
                                    d_embedded = new_signature.node_count + 1
                                    new_signature.node_count += 1
                                    new_signature.iso_labelling[d_embedded] = "FUTURE"
                                    new_signature.embedding.node_dict[d_new] = d_embedded
                                    new_signature.embedding.inverse_node_dict[d_embedded] = d_new

                                    path_list_d.append(([(embedding_node, d_embedded)],
                                                        [(embedding_node, d_embedded)]))

                            if d is not None:
                                # Adding extra nodes in between the paths
                                if extra_node_list:
                                    new_path_list_d = path_list_d.copy()
                                    for existing_path in path_list_d:
                                        # print(f"   original path: {existing_path}")
                                        for i in range(len(extra_node_list)):
                                            j = i + 1
                                            for permutation_tuple in itertools.permutations(extra_node_list, j):
                                                for permutation_element in permutation_tuple:
                                                    # Insert permutation elements in between existing edges
                                                    for count, edge in enumerate(existing_path[0]):
                                                        altered_existing_path = [e for e in existing_path[0] if e != edge]
                                                        altered_existing_edges = [e for e in existing_path[1] if e != edge]

                                                        altered_existing_path.insert(count, (edge[0], permutation_element))
                                                        altered_existing_path.insert(count+1, (permutation_element, edge[1]))
                                                        altered_existing_edges.append((edge[0], permutation_element))
                                                        altered_existing_edges.append((permutation_element, edge[1]))

                                                        new_path_list_d.append((altered_existing_path, altered_existing_edges, tuple(permutation_tuple)))
                                    path_list_d = new_path_list_d

                                # Non-super-compact paths:
                                if not super_compact:
                                    compact_path_list = []
                                    for existing_path in path_list_d:
                                        # Copy the path
                                        if len(existing_path) == 2:
                                            copy_path = (existing_path[0][:], existing_path[1][:])
                                        else:
                                            copy_path = (existing_path[0][:], existing_path[1][:], existing_path[2][:])

                                        # Add another node in between the path
                                        inbetween_edge = copy_path[0].pop(0)
                                        copy_path[0].insert(0, (inbetween_edge[0], new_signature.node_count+13))
                                        copy_path[0].insert(1, (new_signature.node_count+13, inbetween_edge[1]))
                                        inbetween_edge = copy_path[1].pop(0)
                                        copy_path[1].insert(0, (inbetween_edge[0], new_signature.node_count+13))
                                        copy_path[1].insert(1, (new_signature.node_count+13, inbetween_edge[1]))

                                        compact_path_list.append(copy_path)
                                    path_list_d.extend(compact_path_list)

                            if not path_list_a:
                                path_list_a = [None]
                            if not path_list_b:
                                path_list_b = [None]
                            if not path_list_c:
                                path_list_c = [None]
                            if not path_list_d:
                                path_list_d = [None]

                            # print()
                            # print(f"         Loop part:")
                            # print(f"         path_list_a, path_list_b, path_list_c, path_list_d = {path_list_a, path_list_b, path_list_c, path_list_d}")
                            # print(f"         a_new, b_new, c_new, d_new = {a_new, b_new, c_new, d_new}")
                            # print(f"         a, b, c, d = {a, b, c, d}")

                            # TURBO LOOP

                            # Loop A
                            for path_a in path_list_a:
                                # Initiate extra node list for tracking duplicates
                                check_a = False
                                if path_a is not None:
                                    if len(path_a) == 3:
                                        extra_nodes_a = set(path_a[2])
                                        check_a = True

                                # Loop B
                                for path_b in path_list_b:
                                    check_b = False
                                    if path_b is not None:
                                        if len(path_b) == 3:
                                            check_b = True
                                            # Check for duplicates
                                            if check_a:
                                                if any(node in extra_nodes_a for node in path_b[2]):
                                                    continue
                                            extra_nodes_b = set(path_b[2])

                                    # Loop C
                                    for path_c in path_list_c:
                                        check_c = False
                                        if path_c is not None:
                                            if len(path_c) == 3:
                                                check_c = True
                                                # Check for duplicates
                                                if check_a:
                                                    if any(node in extra_nodes_a for node in path_c[2]):
                                                        continue
                                                if check_b:
                                                    if any(node in extra_nodes_b for node in path_c[2]):
                                                        continue
                                                extra_nodes_c = set(path_c[2])

                                        # Loop D
                                        for path_d in path_list_d:
                                            # Check for duplicates
                                            if path_d is not None:
                                                if len(path_d) == 3:
                                                    if check_a:
                                                        if any(node in extra_nodes_a for node in path_d[2]):
                                                            continue
                                                    if check_b:
                                                        if any(node in extra_nodes_b for node in path_d[2]):
                                                            continue
                                                    if check_c:
                                                        if any(node in extra_nodes_c for node in path_d[2]):
                                                            continue

                                            # print(f"         path_a: {path_a}, path_b: {path_b}, path_c: {path_c}, path_d: {path_d}")
                                            path_signature = new_signature.signature_copy()

                                            # A
                                            if path_a is not None:
                                                # Add embeddings
                                                path_signature.embedding.edge_dict[(a_new, new_node)] = path_a[0]
                                                for path_edge in path_a[0]:
                                                    path_signature.embedding.inverse_edge_dict[path_edge] = (a_new, new_node)

                                                # Add edges
                                                for edge in path_a[1]:
                                                    path_signature.network.add_edge(edge[0], edge[1])

                                                # If not super-compact
                                                if not super_compact:
                                                    if path_a[0][-1][0] not in path_signature.iso_labelling:
                                                        path_signature.iso_labelling[path_a[0][-1][0]] = "FUTURE"
                                                        path_signature.node_count += 10

                                            # B
                                            if path_b is not None:
                                                # Add embeddings
                                                path_signature.embedding.edge_dict[(b_new, new_node)] = path_b[0]
                                                for path_edge in path_b[0]:
                                                    path_signature.embedding.inverse_edge_dict[path_edge] = (b_new, new_node)

                                                # Add edges
                                                for edge in path_b[1]:
                                                    path_signature.network.add_edge(edge[0], edge[1])

                                                # If not super-compact
                                                if not super_compact:
                                                    if path_b[0][-1][0] not in path_signature.iso_labelling:
                                                        path_signature.iso_labelling[path_b[0][-1][0]] = "FUTURE"
                                                        path_signature.node_count += 11

                                            # C
                                            if path_c is not None:
                                                # Add embeddings
                                                path_signature.embedding.edge_dict[(new_node, c_new)] = path_c[0]
                                                for path_edge in path_c[0]:
                                                    path_signature.embedding.inverse_edge_dict[path_edge] = (new_node, c_new)

                                                # Add edges
                                                for edge in path_c[1]:
                                                    path_signature.network.add_edge(edge[0], edge[1])

                                                # If not super-compact
                                                if not super_compact:
                                                    if path_c[0][0][1] not in path_signature.iso_labelling:
                                                        path_signature.iso_labelling[path_c[0][0][1]] = "FUTURE"
                                                        path_signature.node_count += 12

                                            # D
                                            if path_d is not None:
                                                # Add embeddings
                                                path_signature.embedding.edge_dict[(new_node, d_new)] = path_d[0]
                                                for path_edge in path_d[0]:
                                                    path_signature.embedding.inverse_edge_dict[path_edge] = (new_node, d_new)

                                                # Add edges
                                                for edge in path_d[1]:
                                                    path_signature.network.add_edge(edge[0], edge[1])

                                                # If not super-compact
                                                if not super_compact:
                                                    if path_d[0][0][1] not in path_signature.iso_labelling:
                                                        path_signature.iso_labelling[path_d[0][0][1]] = "FUTURE"
                                                        path_signature.node_count += 13

                                            if super_compact:
                                                output_list.append(path_signature)

                                            else:
                                                # Add non-super-compact nodes between 2 present nodes.

                                                extra_extra_compact_node_list = [[None], [None], [None], [None]]

                                                temp_parents = list(path_signature.network.predecessors(embedding_node))
                                                temp_children = list(path_signature.network.successors(embedding_node))

                                                for extra_count, parent in enumerate(temp_parents):
                                                    if path_signature.iso_labelling[parent] != "FUTURE":
                                                        continue
                                                    # TODO: I don't know about this one
                                                    if path_signature.network.in_degree[parent] != 1:
                                                        continue
                                                    if parent in path_signature.embedding.inverse_node_dict:
                                                        continue
                                                    for grandparent in path_signature.network.predecessors(
                                                            parent):
                                                        if path_signature.iso_labelling[grandparent] != "FUTURE":
                                                            extra_extra_compact_node_list[extra_count].append((parent, embedding_node))
                                                for extra_count, child in enumerate(temp_children):
                                                    if path_signature.iso_labelling[child] != "FUTURE":
                                                        continue
                                                    # TODO: I don't know about this one
                                                    if path_signature.network.out_degree[child] != 1:
                                                        continue
                                                    if child in path_signature.embedding.inverse_node_dict:
                                                        continue
                                                    grandchildren = tuple(path_signature.network.successors(child))
                                                    for grandchild in grandchildren:
                                                        if path_signature.iso_labelling[grandchild] != "FUTURE":
                                                            extra_extra_compact_node_list[extra_count+2].append((embedding_node, child))

                                                # print(f"extra_extra_compact_node_list = {extra_extra_compact_node_list}")

                                                for aa in extra_extra_compact_node_list[0]:
                                                    for bb in extra_extra_compact_node_list[1]:
                                                        for cc in extra_extra_compact_node_list[2]:
                                                            for dd in extra_extra_compact_node_list[3]:
                                                                less_compact_signature = path_signature.signature_copy()

                                                                if aa is not None:
                                                                    compact_extra_node = less_compact_signature.decompact(aa)
                                                                    less_compact_signature.iso_label(compact_extra_node,"FUTURE")
                                                                    # print(f"aa = {compact_extra_node}")
                                                                if bb is not None:
                                                                    compact_extra_node = less_compact_signature.decompact(bb)
                                                                    less_compact_signature.iso_label(compact_extra_node,"FUTURE")
                                                                    # print(f"bb = {compact_extra_node}")
                                                                if cc is not None:
                                                                    compact_extra_node = less_compact_signature.decompact(cc)
                                                                    less_compact_signature.iso_label(compact_extra_node,"FUTURE")
                                                                    # print(f"cc = {compact_extra_node}")
                                                                if dd is not None:
                                                                    compact_extra_node = less_compact_signature.decompact(dd)
                                                                    less_compact_signature.iso_label(compact_extra_node,"FUTURE")
                                                                    # print(f"dd = {compact_extra_node}")

                                                                output_list.append(less_compact_signature)

                        # NETWORK
                        else:  # If z is in the network

                            extra_node_list = [node for node in extra_node_list if
                                               node != new_node and
                                               node != a and
                                               node != b and
                                               node != c and
                                               node != d]
                            # A
                            if a is not None:
                                if type(a) == int:
                                    a_new = a
                                    # If a is not in the embedding, the path was already added when a was introduced unless z is new
                                    if a in signature.embedding.inverse_node_dict:
                                        a_embedded = new_signature.embedding.inverse_node_dict[a]
                                        new_signature.tree.add_edge(a_embedded, embedding_node)

                                    else:
                                        # Don't use non-embedding nodes, those are instead used as extra nodes.
                                        continue

                                elif a == "new":
                                    a_new = new_signature.node_count + 1
                                    new_signature.node_count += 1
                                    new_signature.iso_labelling[a_new] = "FUTURE"

                                    # If the embedded node has iso-label FUTURE, we can add edges to it (non rooted edgecase)
                                    if new_signature.iso_labelling[embedding_node] == "FUTURE":
                                        a_embedded = new_signature.node_count + 1
                                        new_signature.node_count += 1
                                        new_signature.tree.add_edge(a_embedded, embedding_node)
                                        new_signature.embedding.inverse_node_dict[a_new] = a_embedded
                                        new_signature.embedding.node_dict[a_embedded] = a_new
                                        new_signature.iso_labelling[a_embedded] = "FUTURE"
                                    else:
                                        # If the embedding node is PAST, the edges should have already been added!
                                        continue

                                path_list_a.append(([(a_new, new_node)],))

                                # Adding extra nodes in between the paths
                                if extra_node_list:
                                    # Check if the edge is not in the input network
                                    if not network_in.has_edge(new_signature.iso_labelling[a_new], node_z):
                                        for i in range(len(extra_node_list)):
                                            j = i + 1  # j = 1, 2,..., extra_node_list. Here j is the number of extra nodes used
                                            for permutation_tuple in itertools.permutations(extra_node_list, j):
                                                # Start
                                                altered_path = [(path_list_a[0][0][0][0], permutation_tuple[0])]
                                                # Middle
                                                for count in range(len(permutation_tuple) - 1):
                                                    altered_path.append(
                                                        (permutation_tuple[count], permutation_tuple[count + 1]))
                                                # End
                                                altered_path.append((permutation_tuple[-1], path_list_a[0][0][0][1]))
                                                # Add modified path with tuple of used extra nodes to the path_list
                                                path_list_a.append((altered_path, tuple(permutation_tuple)))

                                # Non-super-compact paths:
                                if not super_compact:
                                    compact_path_list = []
                                    for existing_path in path_list_a:
                                        # Copy the path
                                        if len(existing_path) == 1:
                                            copy_path = (existing_path[0][:],)
                                        else:
                                            copy_path = (existing_path[0][:], existing_path[1][:])

                                        # Add another node in between the path
                                        inbetween_edge = copy_path[0].pop()
                                        copy_path[0].append((inbetween_edge[0], new_signature.node_count+10))
                                        copy_path[0].append((new_signature.node_count+10, inbetween_edge[1]))
                                        compact_path_list.append(copy_path)
                                    path_list_a.extend(compact_path_list)

                            # B
                            if b is not None:
                                if type(b) == int:
                                    b_new = b
                                    # If b is not in the embedding, the path was already added when b was introduced unless z is new
                                    if b in signature.embedding.inverse_node_dict:
                                        b_embedded = new_signature.embedding.inverse_node_dict[b]
                                        new_signature.tree.add_edge(b_embedded, embedding_node)

                                    else:
                                        # Don't use non-embedding nodes, those are instead used as extra nodes.
                                        continue

                                elif b == "new":
                                    b_new = new_signature.node_count + 1
                                    new_signature.node_count += 1
                                    new_signature.iso_labelling[b_new] = "FUTURE"

                                    # If the embedded node has iso-label FUTURE, we can add edges to it (non rooted edgecase)
                                    if new_signature.iso_labelling[embedding_node] == "FUTURE":
                                        b_embedded = new_signature.node_count + 1
                                        new_signature.node_count += 1
                                        new_signature.tree.add_edge(b_embedded, embedding_node)
                                        new_signature.embedding.inverse_node_dict[b_new] = b_embedded
                                        new_signature.embedding.node_dict[b_embedded] = b_new
                                        new_signature.iso_labelling[b_embedded] = "FUTURE"
                                    else:
                                        # If the embedding node is PAST, the edges should have already been added!
                                        continue

                                path_list_b.append(([(b_new, new_node)],))

                                # Adding extra nodes in between the paths
                                if extra_node_list:
                                    # Check if the edge is not in the input network
                                    if not network_in.has_edge(new_signature.iso_labelling[b_new], node_z):
                                        for i in range(len(extra_node_list)):
                                            j = i + 1  # j = 1, 2,..., extra_node_list. Here j is the number of extra nodes used
                                            for permutation_tuple in itertools.permutations(extra_node_list, j):
                                                # Start
                                                altered_path = [(path_list_b[0][0][0][0], permutation_tuple[0])]
                                                # Middle
                                                for count in range(len(permutation_tuple) - 1):
                                                    altered_path.append(
                                                        (permutation_tuple[count], permutation_tuple[count + 1]))
                                                # End
                                                altered_path.append((permutation_tuple[-1], path_list_b[0][0][0][1]))
                                                # Add modified path with tuple of used extra nodes to the path_list
                                                path_list_b.append((altered_path, tuple(permutation_tuple)))

                                # Non-super-compact paths:
                                if not super_compact:
                                    compact_path_list = []
                                    for existing_path in path_list_b:
                                        # Copy the path
                                        if len(existing_path) == 1:
                                            copy_path = (existing_path[0][:],)
                                        else:
                                            copy_path = (existing_path[0][:], existing_path[1][:])

                                        # Add another node inbetween the path
                                        inbetween_edge = copy_path[0].pop()
                                        copy_path[0].append((inbetween_edge[0], new_signature.node_count+11))
                                        copy_path[0].append((new_signature.node_count+11, inbetween_edge[1]))
                                        compact_path_list.append(copy_path)
                                    path_list_b.extend(compact_path_list)

                            # C
                            if c is not None:
                                if type(c) == int:
                                    c_new = c
                                    # If c is not in the embedding, the path was already added when c was introduced unless z is new
                                    if c in signature.embedding.inverse_node_dict:
                                        c_embedded = new_signature.embedding.inverse_node_dict[c]
                                        new_signature.tree.add_edge(embedding_node, c_embedded)

                                    else:
                                        # Don't use non-embedding nodes, those are instead used as extra nodes.
                                        continue

                                elif c == "new":
                                    c_new = new_signature.node_count + 1
                                    new_signature.node_count += 1
                                    new_signature.iso_labelling[c_new] = "FUTURE"

                                    if child_type_dict[0] == "leaf":
                                        c_embedded = c_new
                                        new_signature.tree.add_edge(embedding_node, c_new)
                                        new_signature.embedding.node_dict[c_new] = c_new
                                        new_signature.embedding.inverse_node_dict[c_new] = c_new

                                    else:
                                        # If the embedded node has iso-label FUTURE, we can add edges to it (non rooted edgecase)
                                        if new_signature.iso_labelling[embedding_node] == "FUTURE":
                                            c_embedded = new_signature.node_count + 1
                                            new_signature.node_count += 1
                                            new_signature.tree.add_edge(embedding_node, c_embedded)
                                            new_signature.embedding.inverse_node_dict[c_new] = c_embedded
                                            new_signature.embedding.node_dict[c_embedded] = c_new
                                            new_signature.iso_labelling[c_embedded] = "FUTURE"
                                        else:
                                            # If the embedding node is PAST, the edges should have already been added!
                                            continue

                                path_list_c.append(([(new_node, c_new)],))

                                # Adding extra nodes in between the paths
                                if extra_node_list:
                                    # Check if the edge is not in the input network
                                    if not (network_in.has_edge(node_z, new_signature.iso_labelling[c_new]) or child_type_dict[0] == "leaf"):
                                        for i in range(len(extra_node_list)):
                                            j = i + 1  # j = 1, 2,..., extra_node_list. Here j is the number of extra nodes used
                                            for permutation_tuple in itertools.permutations(extra_node_list, j):
                                                # Start
                                                altered_path = [(path_list_c[0][0][0][0], permutation_tuple[0])]
                                                # Middle
                                                for count in range(len(permutation_tuple)-1):
                                                    altered_path.append((permutation_tuple[count], permutation_tuple[count+1]))
                                                # End
                                                altered_path.append((permutation_tuple[-1], path_list_c[0][0][0][1]))
                                                # Add modified path with tuple of used extra nodes to the path_list
                                                path_list_c.append((altered_path, tuple(permutation_tuple)))

                                # Non-super-compact paths:
                                if not super_compact:
                                    if child_type_dict[0] != "leaf":  # TODO TEST
                                        compact_path_list = []
                                        for existing_path in path_list_c:
                                            # Copy the path
                                            if len(existing_path) == 1:
                                                copy_path = (existing_path[0][:],)
                                            else:
                                                copy_path = (existing_path[0][:], existing_path[1][:])
                                            # Add another node in between the path
                                            inbetween_edge = copy_path[0].pop(0)
                                            copy_path[0].insert(0, (inbetween_edge[0], new_signature.node_count+12))
                                            copy_path[0].insert(1, (new_signature.node_count+12, inbetween_edge[1]))
                                            compact_path_list.append(copy_path)
                                        path_list_c.extend(compact_path_list)

                            # D
                            if d is not None:
                                if type(d) == int:
                                    d_new = d
                                    # If d is not in the embedding, the path was already added when d was introduced unless z is new
                                    if d in signature.embedding.inverse_node_dict:
                                        d_embedded = new_signature.embedding.inverse_node_dict[d]
                                        new_signature.tree.add_edge(embedding_node, d_embedded)

                                    else:
                                        # Don't use non-embedding nodes, those are instead used as extra nodes.
                                        continue

                                elif d == "new":
                                    d_new = new_signature.node_count + 1
                                    new_signature.node_count += 1
                                    new_signature.iso_labelling[d_new] = "FUTURE"

                                    if child_type_dict[1] == "leaf":
                                        d_embedded = d_new
                                        new_signature.tree.add_edge(embedding_node, d_new)
                                        new_signature.embedding.node_dict[d_new] = d_new
                                        new_signature.embedding.inverse_node_dict[d_new] = d_new

                                    else:
                                        # If the embedded node has iso-label FUTURE, we can add edges to it (non rooted edgecase)
                                        if new_signature.iso_labelling[embedding_node] == "FUTURE":
                                            d_embedded = new_signature.node_count + 1
                                            new_signature.node_count += 1
                                            new_signature.tree.add_edge(embedding_node, d_embedded)
                                            new_signature.embedding.inverse_node_dict[d_new] = d_embedded
                                            new_signature.embedding.node_dict[d_embedded] = d_new
                                            new_signature.iso_labelling[d_embedded] = "FUTURE"
                                        else:
                                            # If the embedding node is PAST, the edges should have already been added!
                                            continue

                                path_list_d.append(([(new_node, d_new)],))

                                # Adding extra nodes in between the paths
                                if extra_node_list:
                                    # Check if the edge is not in the input network
                                    if not (network_in.has_edge(node_z, new_signature.iso_labelling[d_new]) or child_type_dict[1] == "leaf"):
                                        for i in range(len(extra_node_list)):
                                            j = i + 1  # j = 1, 2,..., extra_node_list. Here j is the number of extra nodes used
                                            for permutation_tuple in itertools.permutations(extra_node_list, j):
                                                # Start
                                                altered_path = [(path_list_d[0][0][0][0], permutation_tuple[0])]
                                                # Middle
                                                for count in range(len(permutation_tuple)-1):
                                                    altered_path.append((permutation_tuple[count], permutation_tuple[count+1]))
                                                # End
                                                altered_path.append((permutation_tuple[-1], path_list_d[0][0][0][1]))
                                                # Add modified path with tuple of used extra nodes to the path_list
                                                path_list_d.append((altered_path, tuple(permutation_tuple)))

                                # Non-super-compact paths:
                                if not super_compact:
                                    if child_type_dict[1] != "leaf":  # TODO TEST
                                        compact_path_list = []
                                        for existing_path in path_list_d:
                                            # Copy the path
                                            if len(existing_path) == 1:
                                                copy_path = (existing_path[0][:],)
                                            else:
                                                copy_path = (existing_path[0][:], existing_path[1][:])
                                            # Add another node in between the path
                                            inbetween_edge = copy_path[0].pop(0)
                                            copy_path[0].insert(0, (inbetween_edge[0], new_signature.node_count+13))
                                            copy_path[0].insert(1, (new_signature.node_count+13, inbetween_edge[1]))
                                            compact_path_list.append(copy_path)
                                        path_list_d.extend(compact_path_list)

                            if not path_list_a:
                                path_list_a = [None]
                            if not path_list_b:
                                path_list_b = [None]
                            if not path_list_c:
                                path_list_c = [None]
                            if not path_list_d:
                                path_list_d = [None]

                            # TURBO LOOP

                            # Loop A
                            for path_a in path_list_a:
                                # Initiate extra node list for tracking duplicates
                                check_a = False
                                if path_a is not None:
                                    if len(path_a) == 2:
                                        extra_nodes_a = set(path_a[1])
                                        check_a = True

                                # Loop B
                                for path_b in path_list_b:
                                    check_b = False
                                    if path_b is not None:
                                        if len(path_b) == 2:
                                            check_b = True
                                            # Check for duplicates
                                            if check_a:
                                                if any(node in extra_nodes_a for node in path_b[1]):
                                                    continue
                                            extra_nodes_b = set(path_b[1])

                                    # Loop C
                                    for path_c in path_list_c:
                                        check_c = False
                                        if path_c is not None:
                                            if len(path_c) == 2:
                                                check_c = True
                                                # Check for duplicates
                                                if check_a:
                                                    if any(node in extra_nodes_a for node in path_c[1]):
                                                        continue
                                                if check_b:
                                                    if any(node in extra_nodes_b for node in path_c[1]):
                                                        continue
                                                extra_nodes_c = set(path_c[1])

                                        # Loop D
                                        for path_d in path_list_d:
                                            # Check for duplicates
                                            if path_d is not None:
                                                if len(path_d) == 2:
                                                    if check_a:
                                                        if any(node in extra_nodes_a for node in path_d[1]):
                                                            continue
                                                    if check_b:
                                                        if any(node in extra_nodes_b for node in path_d[1]):
                                                            continue
                                                    if check_c:
                                                        if any(node in extra_nodes_c for node in path_d[1]):
                                                            continue

                                            # print(f"         path_a: {path_a}, path_b: {path_b}, path_c: {path_c}, path_d: {path_d}")
                                            path_signature = new_signature.signature_copy()

                                            # A
                                            if path_a is not None:
                                                # Add edges
                                                for edge in path_a[0]:
                                                    path_signature.network.add_edge(edge[0], edge[1])

                                                # Add embedding
                                                path_signature.embedding.edge_dict[(a_embedded, embedding_node)] = path_a[0]
                                                for edge in path_a[0]:
                                                    path_signature.embedding.inverse_edge_dict[edge] = (a_embedded, embedding_node)

                                                # If not super-compact
                                                if not super_compact:
                                                    if path_a[0][-1][0] not in path_signature.iso_labelling:
                                                        path_signature.iso_labelling[path_a[0][-1][0]] = "FUTURE"
                                                        path_signature.node_count += 10

                                            # B
                                            if path_b is not None:
                                                # Add edges
                                                for edge in path_b[0]:
                                                    path_signature.network.add_edge(edge[0], edge[1])

                                                # Add embedding
                                                path_signature.embedding.edge_dict[(b_embedded, embedding_node)] = path_b[0]
                                                for edge in path_b[0]:
                                                    path_signature.embedding.inverse_edge_dict[edge] = (b_embedded, embedding_node)

                                                # If not super-compact
                                                if not super_compact:
                                                    if path_b[0][-1][0] not in path_signature.iso_labelling:
                                                        path_signature.iso_labelling[path_b[0][-1][0]] = "FUTURE"
                                                        path_signature.node_count += 11

                                            # C
                                            if path_c is not None:
                                                # Add edges
                                                for edge in path_c[0]:
                                                    path_signature.network.add_edge(edge[0], edge[1])

                                                # Add embedding
                                                path_signature.embedding.edge_dict[(embedding_node, c_embedded)] = path_c[0]
                                                for edge in path_c[0]:
                                                    path_signature.embedding.inverse_edge_dict[edge] = (embedding_node, c_embedded)

                                                # If not super-compact
                                                if not super_compact:
                                                    if path_c[0][0][1] not in path_signature.iso_labelling:
                                                        path_signature.iso_labelling[path_c[0][0][1]] = "FUTURE"
                                                        path_signature.node_count += 12

                                            # D
                                            if path_d is not None:
                                                # Add edges
                                                for edge in path_d[0]:
                                                    path_signature.network.add_edge(edge[0], edge[1])

                                                # Add embedding
                                                path_signature.embedding.edge_dict[(embedding_node, d_embedded)] = path_d[0]
                                                for edge in path_d[0]:
                                                    path_signature.embedding.inverse_edge_dict[edge] = (embedding_node, d_embedded)

                                                # If not super-compact
                                                if not super_compact:
                                                    if path_d[0][0][1] not in path_signature.iso_labelling:
                                                        path_signature.iso_labelling[path_d[0][0][1]] = "FUTURE"
                                                        path_signature.node_count += 13

                                            if super_compact:
                                                output_list.append(path_signature)

                                            else:
                                                # Add non-super-compact nodes between 2 present nodes.

                                                extra_extra_compact_node_list = [[None], [None], [None], [None]]

                                                temp_parents = list(path_signature.network.predecessors(new_node))
                                                temp_children = list(path_signature.network.successors(new_node))

                                                for extra_count, parent in enumerate(temp_parents):
                                                    if path_signature.iso_labelling[parent] != "FUTURE":
                                                        continue
                                                    # TODO: I don't know about this one
                                                    if path_signature.network.in_degree[parent] != 1:
                                                        continue
                                                    if parent in path_signature.embedding.inverse_node_dict:
                                                        continue
                                                    for grandparent in path_signature.network.predecessors(
                                                            parent):
                                                        if path_signature.iso_labelling[grandparent] != "FUTURE":
                                                            extra_extra_compact_node_list[extra_count].append((parent, new_node))
                                                for extra_count, child in enumerate(temp_children):
                                                    if path_signature.iso_labelling[child] != "FUTURE":
                                                        continue
                                                    # TODO: I don't know about this one
                                                    if path_signature.network.out_degree[child] != 1:
                                                        continue
                                                    if child in path_signature.embedding.inverse_node_dict:
                                                        continue
                                                    grandchildren = tuple(path_signature.network.successors(child))
                                                    for grandchild in grandchildren:
                                                        if path_signature.iso_labelling[grandchild] != "FUTURE":
                                                            extra_extra_compact_node_list[extra_count+2].append((new_node, child))

                                                # print(f"extra_extra_compact_node_list = {extra_extra_compact_node_list}")

                                                for aa in extra_extra_compact_node_list[0]:
                                                    for bb in extra_extra_compact_node_list[1]:
                                                        for cc in extra_extra_compact_node_list[2]:
                                                            for dd in extra_extra_compact_node_list[3]:
                                                                less_compact_signature = path_signature.signature_copy()

                                                                if aa is not None:
                                                                    compact_extra_node = less_compact_signature.decompact(aa)
                                                                    less_compact_signature.iso_label(compact_extra_node,"FUTURE")
                                                                    # print(f"aa = {compact_extra_node}")
                                                                if bb is not None:
                                                                    compact_extra_node = less_compact_signature.decompact(bb)
                                                                    less_compact_signature.iso_label(compact_extra_node,"FUTURE")
                                                                    # print(f"bb = {compact_extra_node}")
                                                                if cc is not None:
                                                                    compact_extra_node = less_compact_signature.decompact(cc)
                                                                    less_compact_signature.iso_label(compact_extra_node,"FUTURE")
                                                                    # print(f"cc = {compact_extra_node}")
                                                                if dd is not None:
                                                                    compact_extra_node = less_compact_signature.decompact(dd)
                                                                    less_compact_signature.iso_label(compact_extra_node,"FUTURE")
                                                                    # print(f"dd = {compact_extra_node}")

                                                                output_list.append(less_compact_signature)


                    # NOT PART OF THE EMBEDDING
                    else:
                        filtered_extra_nodes = [node for node in extra_node_list if
                                                node != new_node and
                                                node != a and
                                                node != b and
                                                node != c and
                                                node != d]

                        if a is not None:
                            if type(a) == tuple:
                                # de-compact edge
                                a_new = new_signature.decompact(a)
                                new_signature.iso_label(a_new, "FUTURE")

                            elif a == "new":
                                a_new = new_signature.node_count + 1
                                new_signature.iso_label(a_new, "FUTURE")
                                new_signature.node_count += 1

                            else:  # If a is an existing node
                                a_new = a

                            path_list_a.append(([(a_new, new_node)],))

                            # Adding extra nodes in between the paths
                            if filtered_extra_nodes:
                                # Check if the edge is not in the input network
                                if not network_in.has_edge(new_signature.iso_labelling[a_new], node_z):
                                    for i in range(len(filtered_extra_nodes)):
                                        j = i + 1  # j = 1, 2,..., filtered_extra_nodes. Here j is the number of extra nodes used
                                        for permutation_tuple in itertools.permutations(filtered_extra_nodes, j):
                                            # Start
                                            altered_path = [(path_list_a[0][0][0][0], permutation_tuple[0])]
                                            # Middle
                                            for count in range(len(permutation_tuple)-1):
                                                altered_path.append((permutation_tuple[count], permutation_tuple[count+1]))
                                            # End
                                            altered_path.append((permutation_tuple[-1], path_list_a[0][0][0][1]))
                                            # Add modified path with tuple of used extra nodes to the path_list
                                            path_list_a.append((altered_path, tuple(permutation_tuple)))

                            # Non-super-compact paths:
                            if not super_compact:
                                compact_path_list = []
                                for existing_path in path_list_a:
                                    # Copy the path
                                    if len(existing_path) == 1:
                                        copy_path = (existing_path[0][:],)
                                    else:
                                        copy_path = (existing_path[0][:], existing_path[1][:])

                                    # Add another node in between the path
                                    inbetween_edge = copy_path[0].pop()
                                    copy_path[0].append((inbetween_edge[0], new_signature.node_count+10))
                                    copy_path[0].append((new_signature.node_count+10, inbetween_edge[1]))
                                    compact_path_list.append(copy_path)
                                path_list_a.extend(compact_path_list)

                        if b is not None:
                            if type(b) == tuple:
                                # Check if the de-compaction edge is identical to that of A
                                if b == a:
                                    # de-compact the bottom new edge created by a
                                    b_new = new_signature.decompact((a_new, b[1]))
                                    new_signature.iso_label(b_new, "FUTURE")

                                # regular de-compaction
                                else:
                                    b_new = new_signature.decompact(b)
                                    new_signature.iso_label(b_new, "FUTURE")

                            elif b == "new":
                                b_new = new_signature.node_count + 1
                                new_signature.iso_label(b_new, "FUTURE")
                                new_signature.node_count += 1

                            else:  # If b is an existing node
                                b_new = b

                            path_list_b.append(([(b_new, new_node)],))

                            # Adding extra nodes in between the paths
                            if filtered_extra_nodes:
                                # Check if the edge is not in the input network
                                if not network_in.has_edge(new_signature.iso_labelling[b_new], node_z):
                                    for i in range(len(filtered_extra_nodes)):
                                        j = i + 1  # j = 1, 2,..., filtered_extra_nodes. Here j is the number of extra nodes used
                                        for permutation_tuple in itertools.permutations(filtered_extra_nodes, j):
                                            # Start
                                            altered_path = [(path_list_b[0][0][0][0], permutation_tuple[0])]
                                            # Middle
                                            for count in range(len(permutation_tuple)-1):
                                                altered_path.append((permutation_tuple[count], permutation_tuple[count+1]))
                                            # End
                                            altered_path.append((permutation_tuple[-1], path_list_b[0][0][0][1]))
                                            # Add modified path with tuple of used extra nodes to the path_list
                                            path_list_b.append((altered_path, tuple(permutation_tuple)))

                            # Non-super-compact paths:
                            if not super_compact:
                                compact_path_list = []
                                for existing_path in path_list_b:
                                    # Copy the path
                                    if len(existing_path) == 1:
                                        copy_path = (existing_path[0][:],)
                                    else:
                                        copy_path = (existing_path[0][:], existing_path[1][:])

                                    # Add another node inbetween the path
                                    inbetween_edge = copy_path[0].pop()
                                    copy_path[0].append((inbetween_edge[0], new_signature.node_count+11))
                                    copy_path[0].append((new_signature.node_count+11, inbetween_edge[1]))
                                    compact_path_list.append(copy_path)
                                path_list_b.extend(compact_path_list)

                        if c is not None:
                            if type(c) == tuple:
                                # Check if the de-compaction edge is identical to that of A
                                if c == b:
                                    # de-compact the bottom new edge created by b
                                    c_new = new_signature.decompact((b_new, c[1]))
                                    new_signature.iso_label(c_new, "FUTURE")
                                elif c == a:
                                    # de-compact the bottom new edge created by a
                                    c_new = new_signature.decompact((a_new, c[1]))
                                    new_signature.iso_label(c_new, "FUTURE")

                                else:
                                    # regular de-compaction
                                    c_new = new_signature.decompact(c)
                                    new_signature.iso_label(c_new, "FUTURE")

                            elif c == "new":
                                c_new = new_signature.node_count + 1
                                new_signature.iso_label(c_new, "FUTURE")
                                new_signature.node_count += 1

                                if child_type_dict[0] == "leaf":
                                    new_signature.tree.add_node(c_new)
                                    new_signature.embedding.node_dict[c_new] = c_new
                                    new_signature.embedding.inverse_node_dict[c_new] = c_new

                            else:  # If c is an existing node
                                c_new = c

                            path_list_c.append(([(new_node, c_new)],))

                            # Adding extra nodes in between the paths
                            if filtered_extra_nodes:
                                # Check if the edge is not in the input network
                                if not network_in.has_edge(node_z, new_signature.iso_labelling[c_new]):
                                    for i in range(len(filtered_extra_nodes)):
                                        j = i + 1  # j = 1, 2,..., filtered_extra_nodes. Here j is the number of extra nodes used
                                        for permutation_tuple in itertools.permutations(filtered_extra_nodes, j):
                                            # Start
                                            altered_path = [(path_list_c[0][0][0][0], permutation_tuple[0])]
                                            # Middle
                                            for count in range(len(permutation_tuple)-1):
                                                altered_path.append((permutation_tuple[count], permutation_tuple[count+1]))
                                            # End
                                            altered_path.append((permutation_tuple[-1], path_list_c[0][0][0][1]))
                                            # Add modified path with tuple of used extra nodes to the path_list
                                            path_list_c.append((altered_path, tuple(permutation_tuple)))

                            # Non-super-compact paths:
                            if not super_compact:
                                compact_path_list = []
                                for existing_path in path_list_c:
                                    # Copy the path
                                    if len(existing_path) == 1:
                                        copy_path = (existing_path[0][:],)
                                    else:
                                        copy_path = (existing_path[0][:], existing_path[1][:])
                                    # Add another node in between the path
                                    inbetween_edge = copy_path[0].pop(0)
                                    copy_path[0].insert(0, (inbetween_edge[0], new_signature.node_count+12))
                                    copy_path[0].insert(1, (new_signature.node_count+12, inbetween_edge[1]))
                                    compact_path_list.append(copy_path)
                                path_list_c.extend(compact_path_list)

                        if d is not None:
                            # de-compact edge
                            if type(d) == tuple:
                                # Check if the de-compaction edge is identical to that of A, B or C
                                if d == c:
                                    # de-compact the bottom new edge created by c
                                    d_new = new_signature.decompact((c_new, d[1]))
                                    new_signature.iso_label(d_new, "FUTURE")
                                elif d == b:
                                    # de-compact the bottom new edge created by b
                                    d_new = new_signature.decompact((b_new, d[1]))
                                    new_signature.iso_label(d_new, "FUTURE")
                                elif d == a:
                                    # de-compact the bottom new edge created by a
                                    d_new = new_signature.decompact((a_new, d[1]))
                                    new_signature.iso_label(d_new, "FUTURE")

                                else:
                                    # regular de-compaction
                                    d_new = new_signature.decompact(d)
                                    new_signature.iso_label(d_new, "FUTURE")

                            elif d == "new":
                                d_new = new_signature.node_count + 1
                                new_signature.iso_label(d_new, "FUTURE")
                                new_signature.node_count += 1

                                if child_type_dict[1] == "leaf":
                                    new_signature.tree.add_node(d_new)
                                    new_signature.embedding.node_dict[d_new] = d_new
                                    new_signature.embedding.inverse_node_dict[d_new] = d_new

                            else:  # If d is an existing node
                                d_new = d

                            path_list_d.append(([(new_node, d_new)],))

                            # Adding extra nodes in between the paths
                            if filtered_extra_nodes:
                                # Check if the edge is not in the input network
                                if not network_in.has_edge(node_z, new_signature.iso_labelling[d_new]):
                                    for i in range(len(filtered_extra_nodes)):
                                        j = i + 1  # j = 1, 2,..., filtered_extra_nodes. Here j is the number of extra nodes used
                                        for permutation_tuple in itertools.permutations(filtered_extra_nodes, j):
                                            # Start
                                            altered_path = [(path_list_d[0][0][0][0], permutation_tuple[0])]
                                            # Middle
                                            for count in range(len(permutation_tuple)-1):
                                                altered_path.append((permutation_tuple[count], permutation_tuple[count+1]))
                                            # End
                                            altered_path.append((permutation_tuple[-1], path_list_d[0][0][0][1]))
                                            # Add modified path with tuple of used extra nodes to the path_list
                                            path_list_d.append((altered_path, tuple(permutation_tuple)))


                            # Non-super-compact paths:
                            if not super_compact:
                                compact_path_list = []
                                for existing_path in path_list_d:
                                    # Copy the path
                                    if len(existing_path) == 1:
                                        copy_path = (existing_path[0][:],)
                                    else:
                                        copy_path = (existing_path[0][:], existing_path[1][:])
                                    # Add another node in between the path
                                    inbetween_edge = copy_path[0].pop(0)
                                    copy_path[0].insert(0, (inbetween_edge[0], new_signature.node_count+13))
                                    copy_path[0].insert(1, (new_signature.node_count+13, inbetween_edge[1]))
                                    compact_path_list.append(copy_path)
                                path_list_d.extend(compact_path_list)

                        # CONSTRUCT THE EDGES

                        if not path_list_a:
                            path_list_a = [None]
                        if not path_list_b:
                            path_list_b = [None]
                        if not path_list_c:
                            path_list_c = [None]
                        if not path_list_d:
                            path_list_d = [None]

                        # print()
                        # print("         Loop part:")
                        # print(f"         path_list_a: {path_list_a}")
                        # print(f"         path_list_b: {path_list_b}")
                        # print(f"         path_list_b: {path_list_c}")
                        # print(f"         path_list_b: {path_list_d}")

                        # print(f"         a_new, b_new, c_new, d_new = {a_new, b_new, c_new, d_new}")
                        # print(f"         a, b, c, d = {a, b, c, d}")

                        # TURBO LOOP

                        # Loop A
                        for path_a in path_list_a:
                            # Initiate extra node list for tracking duplicates
                            check_a = False
                            if path_a is not None:
                                if len(path_a) == 2:
                                    extra_nodes_a = set(path_a[1])
                                    check_a = True

                            # Loop B
                            for path_b in path_list_b:
                                check_b = False
                                if path_b is not None:
                                    if len(path_b) == 2:
                                        # a and b cannot both be embedding arcs, so they cannot both have extra nodes
                                        if check_a:
                                            continue
                                        check_b = True
                                        # Check for duplicates
                                        extra_nodes_b = set(path_b[1])

                                # Loop C
                                for path_c in path_list_c:
                                    check_c = False
                                    if path_c is not None:
                                        if len(path_c) == 2:
                                            check_c = True
                                            # Check for duplicates
                                            if check_a:
                                                if any(node in extra_nodes_a for node in path_c[1]):
                                                    continue
                                            elif check_b:
                                                if any(node in extra_nodes_b for node in path_c[1]):
                                                    continue
                                            extra_nodes_c = set(path_c[1])

                                    # Loop D
                                    for path_d in path_list_d:
                                        check_d = False
                                        if path_d is not None:
                                            if len(path_d) == 2:
                                                check_d = True
                                                # c and d cannot both be embedding arcs, so they cannot both have extra nodes
                                                if check_c:
                                                    continue
                                                # Check for duplicates
                                                if check_a:
                                                    if any(node in extra_nodes_a for node in path_d[1]):
                                                        continue
                                                if check_b:
                                                    if any(node in extra_nodes_b for node in path_d[1]):
                                                        continue

                                        # print(f"         path_a: {path_a}, path_b: {path_b}, path_c: {path_c}, path_d: {path_d}")
                                        path_signature = new_signature.signature_copy()

                                        # A
                                        if path_a is not None:
                                            # Add edges
                                            for edge in path_a[0]:
                                                path_signature.network.add_edge(edge[0], edge[1])

                                            # If not super-compact
                                            if not super_compact:
                                                if path_a[0][-1][0] not in path_signature.iso_labelling:
                                                    path_signature.iso_labelling[path_a[0][-1][0]] = "FUTURE"
                                                    path_signature.node_count += 10

                                        # B
                                        if path_b is not None:
                                            # Add edges
                                            for edge in path_b[0]:
                                                path_signature.network.add_edge(edge[0], edge[1])

                                            # If not super-compact
                                            if not super_compact:
                                                if path_b[0][-1][0] not in path_signature.iso_labelling:
                                                    path_signature.iso_labelling[path_b[0][-1][0]] = "FUTURE"
                                                    path_signature.node_count += 11
                                        # C
                                        if path_c is not None:
                                            # Add edges
                                            for edge in path_c[0]:
                                                path_signature.network.add_edge(edge[0], edge[1])

                                            # If not super-compact
                                            if not super_compact:
                                                if path_c[0][0][1] not in path_signature.iso_labelling:
                                                    path_signature.iso_labelling[path_c[0][0][1]] = "FUTURE"
                                                    path_signature.node_count += 12
                                        # D
                                        if path_d is not None:
                                            # Add edges
                                            for edge in path_d[0]:
                                                path_signature.network.add_edge(edge[0], edge[1])

                                            # If not super-compact
                                            if not super_compact:
                                                if path_d[0][0][1] not in path_signature.iso_labelling:
                                                    path_signature.iso_labelling[path_d[0][0][1]] = "FUTURE"
                                                    path_signature.node_count += 13

                                        # EMBEDDING PART
                                        edgecase = False

                                        # Option 0: Check for existing embeddings (happens through de-compacting):
                                        already_embedding = False  # Initial value (remains if unchanged)
                                        for parent in path_signature.network.predecessors(new_node):
                                            # Check through incoming edges
                                            if (parent, new_node) in path_signature.embedding.inverse_edge_dict:
                                                already_embedding = True
                                                # print("            Already has an edge embedding")

                                            else:
                                                # Check if non-embedding edge does not go to an embedding node (edgecase 5)
                                                if parent in path_signature.embedding.inverse_node_dict:
                                                    # print(f"            Edgecase 5: embedding node {parent} has no embedded edge to it")
                                                    edgecase = True

                                        if already_embedding:
                                            # Check for non-embedding leaf edge (edgecase 1)
                                            if network_in.out_degree(node_z) == 2:
                                                if child_type_dict[0] == "leaf" or child_type_dict[1] == "leaf":
                                                    for network_child in path_signature.network.successors(new_node):
                                                        # If the node is a leaf
                                                        if network_child in path_signature.tree:
                                                            # If the node has no edge in the tree and thus no embedding
                                                            if path_signature.tree.in_degree(network_child) == 0:
                                                                edgecase = True
                                                                # print(f"            Edgecase 1: no embedded path to leaf {network_child}")

                                            # Pass the signature if it already has a path embedding (and not the edgecase)
                                            if not edgecase:
                                                # print(f"            node {new_node} already had a path embedding")
                                                # Check if the children don't get two embedded edges (space issue) (edgecase)
                                                # This can happen when there's an compacted node who's arc contains a child
                                                if type(c) == int and type(d) == tuple:
                                                    if d[1] == c:
                                                        # Check if there exists a double embedding now:
                                                        embedding1 = False
                                                        embedding2 = False  #  TODO: slow
                                                        for path in path_signature.embedding.edge_dict.values():
                                                            if (new_node, c) in path:
                                                                embedding1 = True

                                                            if (d[1], c) in path:
                                                                embedding2 = True

                                                        if embedding1 and embedding2:
                                                            # print("   decompacted into the same child gives bad embeddings (edgecase ?)")
                                                            continue
                                                if type(d) == int and type(c) == tuple:
                                                    if c[1] == d:
                                                        # Check if there exists a double embedding now:
                                                        embedding1 = False
                                                        embedding2 = False  #  TODO: slow
                                                        for path in path_signature.embedding.edge_dict.values():
                                                            if (new_node, d) in path:
                                                                embedding1 = True
                                                            if (c[1], d) in path:
                                                                embedding2 = True
                                                        if embedding1 and embedding2:
                                                            # print("   decompacted into the same child gives bad embeddings (edgecase ?)")
                                                            continue
                                                output_list.append(path_signature)
                                                # print("   Success (already had an embedding)")

                                        else:
                                            # Option 1: Add no embedding (don't do this if a child is a leaf or a parent/child is an embedding):
                                            if "leaf" not in child_type_dict.values() and not edgecase and (not check_a and not check_b and not check_c and not check_d):  # TODO: edgecase = experimental, len(used_extra_nodes) == 0 also
                                                output_list.append(path_signature)


                                            # Option 2: Add different embeddings:
                                            for i, path_parent in enumerate([a_new, b_new]):
                                                for j, path_child in enumerate([c_new, d_new]):
                                                    if path_parent is None or path_child is None:
                                                        continue
                                                    # print("               Inner loop (for embeddings)")
                                                    # # Don't create the embedding if the parent already existed but has no embedding edge to the node
                                                    # if [a, b][i] != "new":
                                                    #     if ([a, b][i], new_node) not in signature.embedding.inverse_edge_dict:
                                                    #         print([a, b][i])
                                                    #         continue

                                                    embedding_signature = path_signature.signature_copy()
                                                    # print(f"               path_parent = {path_parent}, path_child = {path_child}")

                                                    # Check if path_parent or path_child are already ends of embedded paths but not embedded (Edgecase 4)
                                                    problem = False
                                                    for path_end in [path_parent, path_child]:
                                                        if path_end in embedding_signature.embedding.inverse_node_dict:
                                                            continue
                                                        # TODO: this is slow...
                                                        for embedded_path in embedding_signature.embedding.edge_dict.values():
                                                            for embedded_edge in embedded_path:
                                                                if path_end in embedded_edge:
                                                                    problem = True

                                                    if problem:
                                                        # print(f"            No embedding edge available for node {[path_parent, path_child]}")
                                                        continue

                                                    # A
                                                    if i == 0:
                                                        if type(a) == int:
                                                            if a in embedding_signature.embedding.inverse_node_dict:
                                                                e = embedding_signature.embedding.inverse_node_dict[a]  # TODO: check if we don't need some recursive function to find this if the parent also has no embedding...
                                                            else:
                                                                e = embedding_signature.node_count + 1
                                                                embedding_signature.node_count += 1
                                                                embedding_signature.iso_label(e, "FUTURE")

                                                        else:
                                                            e = embedding_signature.node_count + 1
                                                            embedding_signature.node_count += 1
                                                            embedding_signature.iso_label(e, "FUTURE")

                                                    # B
                                                    else:
                                                        if type(b) == int:
                                                            if b in embedding_signature.embedding.inverse_node_dict:
                                                                e = embedding_signature.embedding.inverse_node_dict[b]
                                                                # TODO: check if we don't need some recursive function to find this if the parent also has no embedding...
                                                            else:
                                                                e = embedding_signature.node_count + 1
                                                                embedding_signature.node_count += 1
                                                                embedding_signature.iso_label(e, "FUTURE")
                                                        else:
                                                            e = embedding_signature.node_count + 1
                                                            embedding_signature.node_count += 1
                                                            embedding_signature.iso_label(e, "FUTURE")

                                                    # If the other child is a leaf or already an embedding node (edgecase 8), don't create another embedding
                                                    if 1 in child_type_dict:  # Check if there's even 2 children
                                                        if child_type_dict[1-j] == "leaf" or [c_new, d_new][1-j] in embedding_signature.embedding.inverse_node_dict:
                                                            continue

                                                    if child_type_dict[j] == "leaf":
                                                        # print("               leaf!")
                                                        f = path_child

                                                        # TODO: test this!
                                                        parent_path = [path_a, path_b][i]
                                                        child_path = [path_c, path_d][j]

                                                        if parent_path is not None and child_path is not None:
                                                            parent_path = parent_path[0]
                                                            child_path = child_path[0]
                                                            combined_path = parent_path.copy()
                                                            combined_path.extend(child_path)
                                                            embedding_signature.embedding.edge_dict[(e, f)] = combined_path
                                                            for edge in combined_path:
                                                                embedding_signature.embedding.inverse_edge_dict[edge] = (e, f)

                                                        else:
                                                            embedding_signature.embedding.edge_dict[(e, f)] = [(path_parent, new_node), (new_node, path_child)]
                                                            embedding_signature.embedding.inverse_edge_dict[(path_parent, new_node)] = (e, f)
                                                            embedding_signature.embedding.inverse_edge_dict[(new_node, path_child)] = (e, f)

                                                    else:
                                                        original_c_or_d = [c, d][j]
                                                        if original_c_or_d == 'new':
                                                            f = embedding_signature.node_count + 1
                                                            embedding_signature.node_count += 1
                                                            embedding_signature.embedding.node_dict[f] = path_child
                                                            embedding_signature.embedding.inverse_node_dict[path_child] = f
                                                            embedding_signature.iso_label(f, "FUTURE")

                                                        # C & D
                                                        # Embedded
                                                        if path_child in embedding_signature.embedding.inverse_node_dict:
                                                            f = embedding_signature.embedding.inverse_node_dict[path_child]

                                                            embedding_signature.embedding.node_dict[f] = path_child
                                                            embedding_signature.embedding.inverse_node_dict[path_child] = f

                                                            parent_path = [path_a, path_b][i]
                                                            child_path = [path_c, path_d][j]

                                                            if parent_path is not None and child_path is not None:
                                                                # print("               New way")
                                                                parent_path = parent_path[0]
                                                                child_path = child_path[0]
                                                                combined_path = parent_path.copy()
                                                                combined_path.extend(child_path)
                                                                embedding_signature.embedding.edge_dict[(e, f)] = combined_path
                                                                # print(f"               parent_path = {parent_path}")
                                                                # print(f"               child_path = {child_path}")
                                                                # print(f"               combined_path = {combined_path}")
                                                                for edge in combined_path:
                                                                    embedding_signature.embedding.inverse_edge_dict[edge] = (e, f)

                                                            else:
                                                                embedding_signature.embedding.edge_dict[(e, f)] = [(path_parent, new_node), (new_node, path_child)]
                                                                embedding_signature.embedding.inverse_edge_dict[(path_parent, new_node)] = (e, f)
                                                                embedding_signature.embedding.inverse_edge_dict[(new_node, path_child)] = (e, f)

                                                            # TODO: check if we don't need some recursive function to find this if the child also has no embedding...

                                                        # Not embedded  (Edgecase 10?)
                                                        else:
                                                            extender_node = embedding_signature.node_count + 1
                                                            f = embedding_signature.node_count + 2
                                                            embedding_signature.node_count += 2
                                                            embedding_signature.iso_label(extender_node, "FUTURE")
                                                            embedding_signature.iso_label(f, "FUTURE")
                                                            embedding_signature.network.add_edge(path_child, extender_node)

                                                            embedding_signature.embedding.node_dict[f] = extender_node
                                                            embedding_signature.embedding.inverse_node_dict[extender_node] = f

                                                            parent_path = [path_a, path_b][i]
                                                            child_path = [path_c, path_d][j]

                                                            if parent_path is not None and child_path is not None:
                                                                parent_path = parent_path[0]
                                                                child_path = child_path[0]

                                                                combined_path = parent_path.copy()
                                                                combined_path.extend(child_path)
                                                                combined_path.append((path_child, extender_node))

                                                                embedding_signature.embedding.edge_dict[(e, f)] = combined_path
                                                                for edge in combined_path:
                                                                    embedding_signature.embedding.inverse_edge_dict[edge] = (e, f)

                                                            else:
                                                                embedding_signature.embedding.edge_dict[(e, f)] = [(path_parent, new_node), (new_node, path_child), (path_child, extender_node)]
                                                                embedding_signature.embedding.inverse_edge_dict[(path_parent, new_node)] = (e, f)
                                                                embedding_signature.embedding.inverse_edge_dict[(new_node, path_child)] = (e, f)
                                                                embedding_signature.embedding.inverse_edge_dict[(path_child, extender_node)] = (e, f)

                                                    # print(f"               e = {e}, f = {f}")

                                                    embedding_signature.tree.add_edge(e, f)

                                                    embedding_signature.embedding.node_dict[e] = path_parent
                                                    embedding_signature.embedding.inverse_node_dict[path_parent] = e

                                                    # Check if any children have 2 embedding incoming edges:
                                                    problem = False
                                                    for child in embedding_signature.network.successors(new_node):
                                                        if len([child_parent for child_parent in embedding_signature.network.predecessors(child) if (child_parent, child) in embedding_signature.embedding.inverse_edge_dict]) == 2:
                                                            # print(f"               Child {child} has too many embeddings", embedding_signature.embedding.edge_dict)
                                                            problem = True
                                                            break
                                                    if problem:
                                                        break

                                                    # if list(embedding_signature.network.edges()).sort() == [(1, 3), (1, 4),
                                                    #                                                    (2, 1), (2, 3),
                                                    #                                                    (3, 4), (4, 6),
                                                    #                                                    (5, 2)] and len(
                                                    #         embedding_signature.tree.edges()) == 0:
                                                    #     TreeContainmentTools.signature_image(embedding_signature, 9002)
                                                    output_list.append(embedding_signature)

                        if not super_compact:
                            temp_output_list = []

                            # Add non-super-compact nodes between 2 present nodes.

                            for path_signature in output_list:
                                extra_extra_compact_node_list = [[None], [None], [None], [None]]

                                temp_parents = list(path_signature.network.predecessors(new_node))
                                temp_children = list(path_signature.network.successors(new_node))

                                for extra_count, parent in enumerate(temp_parents):
                                    if path_signature.iso_labelling[parent] != "FUTURE":
                                        continue
                                    # TODO: I don't know about this one
                                    if path_signature.network.in_degree[parent] != 1:
                                        continue
                                    if parent in path_signature.embedding.inverse_node_dict:
                                        continue
                                    if (parent, new_node) not in signature.embedding.inverse_edge_dict:
                                        continue
                                    for grandparent in path_signature.network.predecessors(
                                            parent):
                                        if path_signature.iso_labelling[grandparent] != "FUTURE":
                                            extra_extra_compact_node_list[extra_count].append((parent, new_node))
                                for extra_count, child in enumerate(temp_children):
                                    if path_signature.iso_labelling[child] != "FUTURE":
                                        continue
                                    # TODO: I don't know about this one
                                    if path_signature.network.out_degree[child] != 1:
                                        continue
                                    if child in path_signature.embedding.inverse_node_dict:
                                        continue
                                    if (new_node, child) not in signature.embedding.inverse_edge_dict:
                                        continue
                                    grandchildren = tuple(path_signature.network.successors(child))
                                    for grandchild in grandchildren:
                                        if path_signature.iso_labelling[grandchild] != "FUTURE":
                                            extra_extra_compact_node_list[extra_count + 2].append((new_node, child))

                                # print(f"extra_extra_compact_node_list = {extra_extra_compact_node_list}")

                                for aa in extra_extra_compact_node_list[0]:
                                    for bb in extra_extra_compact_node_list[1]:
                                        for cc in extra_extra_compact_node_list[2]:
                                            for dd in extra_extra_compact_node_list[3]:
                                                less_compact_signature = path_signature.signature_copy()

                                                if aa is not None:
                                                    compact_extra_node = less_compact_signature.decompact(aa)
                                                    less_compact_signature.iso_label(compact_extra_node, "FUTURE")
                                                    # print(f"aa = {compact_extra_node}")
                                                if bb is not None:
                                                    compact_extra_node = less_compact_signature.decompact(bb)
                                                    less_compact_signature.iso_label(compact_extra_node, "FUTURE")
                                                    # print(f"bb = {compact_extra_node}")
                                                if cc is not None:
                                                    compact_extra_node = less_compact_signature.decompact(cc)
                                                    less_compact_signature.iso_label(compact_extra_node, "FUTURE")
                                                    # print(f"cc = {compact_extra_node}")
                                                if dd is not None:
                                                    compact_extra_node = less_compact_signature.decompact(dd)
                                                    less_compact_signature.iso_label(compact_extra_node, "FUTURE")
                                                    # print(f"dd = {compact_extra_node}")

                                                temp_output_list.append(less_compact_signature)
                            output_list = temp_output_list

    return output_list
