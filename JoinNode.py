import networkx as nx
import itertools
import TreeDecomposition
import TreeContainmentTools
import NetworkIsomorphismTools
import copy  # TODO I don't like this
import TreeContainmentChecks
import IntroduceNode
import TreeContainment


def on_the_fly_checking(network_in, tree_in, signature):
    """This procedure function checks a signature to see there are leaves that can be changed "on the fly".
    It returns a list of nodes that it is unsure about"""
    # print()
    # print("On the fly checking signature")
    unsure_nodes = []
    for node in signature.tree.nodes():
        do_not_process = False  # Used to make sure network-side checks are not done in case of tree-side success
        # Check for potential leaves from the tree side
        if signature.iso_labelling[node] == "FUTURE":
            if signature.tree.in_degree(node) == 1 and signature.tree.out_degree(node) == 0:
                # Skip if it's already a leaf
                if node in signature.network:
                    continue

                # Check if its embedding is also potentially a leaf
                embedding_node = signature.embedding.node_dict[node]
                if signature.network.in_degree(embedding_node) == 1 and signature.network.out_degree(embedding_node) == 0:

                    # Check the tree parent
                    for parent in signature.tree.predecessors(node):  # Only 1
                        if signature.iso_labelling[parent] == "FUTURE":  # PAST is impossible
                            continue
                        iso_parent = signature.iso_labelling[parent]

                        # Check parents children in D_IN
                        leaf_list = []
                        for potential_child in tree_in.successors(iso_parent):
                            if potential_child in network_in:
                                leaf_list.append(potential_child)

                        # Stop if there's no leaves at all
                        if not leaf_list:
                            do_not_process = True
                            continue

                        # If all children should be leaves
                        if len(leaf_list) == tree_in.out_degree(iso_parent):
                            on_the_fly_changing(node, signature)
                            do_not_process = True
                            break

                        # If not all children should be leaves
                        else:

                            # Check the other child in the display graph:
                            for child in signature.tree.successors(parent):
                                if child != node:
                                    # Check if the other child is already a leaf:
                                    if child in signature.network:
                                        continue
                                    # If the other node CAN become a leaf
                                    if signature.tree.out_degree(child) == 0 and signature.tree.in_degree(child) == 1:
                                        continue

                                    on_the_fly_changing(node, signature)
                                    do_not_process = True
                                    break
                    if do_not_process:
                        continue

                    # Try network side checks
                    for parent in signature.network.predecessors(embedding_node):
                        if signature.iso_labelling[parent] == "FUTURE" or signature.iso_labelling[parent] == "PAST":
                            continue
                        iso_parent = signature.iso_labelling[parent]

                        # Check parents children in D_IN
                        leaf_list = []
                        for potential_child in network_in.successors(iso_parent):
                            if potential_child in tree_in:
                                leaf_list.append(potential_child)

                        # Stop if there's no leaves at all
                        if not leaf_list:
                            continue


                        # If all children should be leaves
                        if len(leaf_list) == network_in.out_degree(iso_parent):
                            on_the_fly_changing(node, signature)
                            do_not_process = True
                            break

                        # If not all children should be leaves
                        else:
                            # Check the other child in the display graph:
                            for child in signature.network.successors(parent):
                                if child != embedding_node:
                                    # Check if the other child is already a leaf:
                                    if child not in signature.tree:
                                        on_the_fly_changing(node, signature)
                                        do_not_process = True
                                        break
                    if do_not_process:
                        continue
                    unsure_nodes.append(node)
    # print(f"unsure_nodes: {unsure_nodes}")
    return unsure_nodes


def on_the_fly_changing(node, signature):
    """This procedure function requires a tree node and changes it into a leaf "on the fly".
    It returns False if the resulting signature is not valid."""

    embedding_node = signature.embedding.node_dict[node]

    # Grab parents from both sides
    for network_parent in signature.network.predecessors(embedding_node):  # There is only 1 parent
        for tree_parent in signature.tree.predecessors(node):  # There is only 1 parent
            # Remove the network node and attach its parent to the changed leaf
            signature.network.remove_node(embedding_node)
            signature.iso_labelling.pop(embedding_node)
            signature.embedding.inverse_node_dict.pop(embedding_node)

            signature.network.add_edge(network_parent, node)
            embedding_path = signature.embedding.edge_dict[(tree_parent, node)]

            removed_edge = embedding_path.pop()  # Remove last item

            # if removed_edge not in signature.embedding.inverse_edge_dict:
            #     # print(f"removed edge {removed_edge}")
            #     signature.print(1337)
            #     TreeContainmentTools.signature_image(signature, 1337)

            signature.embedding.inverse_edge_dict.pop(removed_edge)
            embedding_path.append((network_parent, node))
            signature.embedding.edge_dict[(tree_parent, node)] = embedding_path
            signature.embedding.inverse_edge_dict[(network_parent, node)] = (tree_parent, node)
            signature.embedding.node_dict[node] = node
            signature.embedding.inverse_node_dict[node] = node

    # TODO: consider doing a check here to see if there exists a node in the input display graph with the treeside parent and the networkside parent that the given node has.
    return


def join_node(network_in, tree_in, bag1, bag2):
    output_list = []

    # print(f"bag1 has size {len(bag1)}")
    # print(f"bag2 has size {len(bag2)}\n")

    # Prepare bag1
    signature_dict1 = {}
    sub_signature_dict1 = {}

    for count, signature in enumerate(bag1):
        signature = signature.signature_copy()  # I have no idea why this is needed, but removing it causes issues

        # print(f"Preparing bag 1 signature {count}")
        unsure_node_list = on_the_fly_checking(network_in, tree_in, signature)
        # print(f"unsure_node_list: {unsure_node_list}")
        try_list = [signature]
        for node in unsure_node_list:
            max_iteration = len(try_list)
            for i in range(max_iteration):
                new_signature = try_list[i].signature_copy()
                on_the_fly_changing(node, new_signature)
                try_list.append(new_signature)
        signature_dict1[count] = tuple(try_list)
        sub_list = []
        for try_signature in try_list:
            sub_signature = try_signature.signature_copy()
            past_to_future_restriction(sub_signature)
            sub_list.append(sub_signature)
        sub_signature_dict1[count] = tuple(sub_list)

    # Prepare bag2
    signature_dict2 = {}
    sub_signature_dict2 = {}

    for count, signature in enumerate(bag2):
        signature = signature.signature_copy()  # I have no idea why this is needed, but removing it causes issues
        # print(f"Preparing bag 1 signature {count}")
        unsure_node_list = on_the_fly_checking(network_in, tree_in, signature)
        # print(f"unsure_node_list: {unsure_node_list}")
        try_list = [signature]
        for node in unsure_node_list:
            max_iteration = len(try_list)
            for i in range(max_iteration):
                new_signature = try_list[i].signature_copy()
                on_the_fly_changing(node, new_signature)
                try_list.append(new_signature)
        signature_dict2[count] = tuple(try_list)
        sub_list = []
        for try_signature in try_list:
            sub_signature = try_signature.signature_copy()
            past_to_future_restriction(sub_signature)
            sub_list.append(sub_signature)
        sub_signature_dict2[count] = tuple(sub_list)

    for count1 in signature_dict1:
        for count2 in signature_dict2:
            # print(f"\nTRYING SIGNATURES {count1} AND {count2}:")
            success = False
            for sub_count1, signature1 in enumerate(signature_dict1[count1]):
                sub_signature1 = sub_signature_dict1[count1][sub_count1]
                for sub_count2, signature2 in enumerate(signature_dict2[count2]):
                    sub_signature2 = sub_signature_dict2[count2][sub_count2]

                    temp_output = signature_joiner2(signature1, signature2, sub_signature1, sub_signature2)
                    if temp_output is not False:
                        output_list.append(temp_output)
                        success = True
                        break
                if success:
                    break

    # TODO: Old stuff
    # for count1, signature1 in enumerate(bag1):
    #     for count2, signature2 in enumerate(bag2):
    #
    #         new_signature1 = signature1.signature_copy()
    #         new_signature2 = signature2.signature_copy()
    #
    #         print(f"\nTRYING SIGNATURES {count1} AND {count2}:")
    #
    #         unsure_node_list_1 = on_the_fly_checking(network_in, tree_in, new_signature1)
    #         unsure_node_list_2 = on_the_fly_checking(network_in, tree_in, new_signature2)
    #
    #         print(f"unsure_node_list_1: {unsure_node_list_1}")
    #         print(f"unsure_node_list_2: {unsure_node_list_2}")
    #
    #         # TODO: try finding some more intelligent way of doing this?
    #         # Try every option
    #         try_list_1 = [new_signature1]
    #         try_list_2 = [new_signature2]
    #
    #         for node in unsure_node_list_1:
    #             max_iteration = len(try_list_1)
    #             for i in range(max_iteration):
    #                 new_signature = try_list_1[i].signature_copy()
    #                 on_the_fly_changing(node, new_signature)
    #                 try_list_1.append(new_signature)
    #
    #         for node in unsure_node_list_2:
    #             max_iteration = len(try_list_2)
    #             for i in range(max_iteration):
    #                 new_signature = try_list_2[i].signature_copy()
    #                 on_the_fly_changing(node, new_signature)
    #                 try_list_2.append(new_signature)
    #
    #         success = False
    #         for try_signature_1 in try_list_1:
    #             for try_signature_2 in try_list_2:
    #                 temp_output = signature_joiner2(try_signature_1, try_signature_2)
    #                 if temp_output is not False:
    #                     output_list.append(temp_output)
    #                     success = True
    #                     break
    #             if success:
    #                 break

    return output_list


def join_path_finder(signature):
    """ This function constructs and returns the mega_dict.
    It contains paths of length 2 within the signature"""

    # Mega dict:
    # - "two_path_parents" contains parent labels
    # - "two_path_children" contains children labels
    # - "network_starts" and "network_ends" contain lists of parents for a given start node
    # - "tree_starts" and "tree_ends" contain a parent for a given start node

    mega_dict = {"two_path_parents": {}, "two_path_children": {}, "network_starts": {}, "network_ends": {}, "tree_starts": {}, "tree_ends": {}}

    # Finding start/end nodes in tree
    for node in signature.tree.nodes():
        if signature.iso_labelling[node] == "PAST":
            # Check for nodes at the start of path:
            if signature.tree.in_degree(node) == 0 and signature.tree.out_degree(node) == 1:
                temp_list = []
                for child in signature.tree.successors(node):
                    if signature.iso_labelling[child] == "PAST":
                        for child_child in signature.tree.successors(child):
                            child_child_label = signature.iso_labelling[child_child]
                            if child_child_label != "FUTURE" and child_child_label != "PAST":
                                temp_list.append(child_child_label)
                if temp_list:
                    mega_dict["tree_starts"][node] = temp_list

            # Check for nodes at the end of path:
            if signature.tree.in_degree(node) == 1 and signature.tree.out_degree(node) == 0:
                for parent in signature.tree.predecessors(node):
                    if signature.iso_labelling[parent] == "PAST":
                        # Check if it's not a leaf (TODO: intuition, not checked)
                        if node not in signature.network:
                            for parent_parent in signature.tree.predecessors(parent):
                                parent_parent_label = signature.iso_labelling[parent_parent]
                                if parent_parent_label != "FUTURE" and parent_parent_label != "PAST":
                                    mega_dict["tree_ends"][node] = parent_parent_label

    two_path_list = []
    # Finding start/end nodes in network
    for node in signature.network.nodes():
        if signature.iso_labelling[node] == "PAST":
            if node in signature.embedding.inverse_node_dict:
                # Check for nodes at the start of path:
                if signature.network.in_degree(node) == 0 and signature.network.out_degree(node) == 1:
                    for child in signature.network.successors(node):
                        if signature.iso_labelling[child] == "PAST":
                            if child in signature.embedding.inverse_node_dict:
                                temp_options = []
                                for child_child in signature.network.successors(child):
                                    child_child_label = signature.iso_labelling[child_child]
                                    if child_child_label != "FUTURE" and child_child_label != "PAST":
                                        temp_options.append(child_child_label)
                                if temp_options:
                                    mega_dict["network_starts"][node] = temp_options

                # Check for nodes at the end of path:
                if signature.network.in_degree(node) == 1 and signature.network.out_degree(node) == 0:
                    for parent in signature.network.predecessors(node):
                        if signature.iso_labelling[parent] == "PAST":
                            if parent in signature.embedding.inverse_node_dict:
                                temp_options = []
                                for parent_parent in signature.network.predecessors(parent):
                                    parent_parent_label = signature.iso_labelling[parent_parent]
                                    if parent_parent_label != "FUTURE" and parent_parent_label != "PAST":
                                        temp_options.append(parent_parent_label)
                                if temp_options:
                                    mega_dict["network_ends"][node] = temp_options

            else:
                # Check for paths of length 2
                # TODO: should this node be part of some embedding path?
                if signature.network.out_degree(node) == 1 and signature.network.in_degree(node) == 1:
                    for child in signature.network.successors(node):
                        if signature.iso_labelling[child] == "PAST":
                            two_path_list.append((node, child))
                    for parent in signature.network.predecessors(node):
                        if signature.iso_labelling[parent] == "PAST":
                            two_path_list.append((parent, node))

    # Checking to find parents of two-long paths
    for two_path in two_path_list:
        # Checking parents of two-long paths
        temp_options = []
        for parent in signature.network.predecessors(two_path[0]):
            parent_label = signature.iso_labelling[parent]
            if parent_label != "FUTURE" and parent_label != "PAST":
                temp_options.append(parent_label)

        if temp_options:
            mega_dict["two_path_parents"][two_path] = temp_options
            # Skip child search if a parent was found
            continue

        # Checking children of two-long paths
        temp_options = []
        for child in signature.network.successors(two_path[1]):
            child_label = signature.iso_labelling[child]
            if child_label != "FUTURE" and child_label != "PAST":
                temp_options.append(child_label)

        if temp_options:
            mega_dict["two_path_children"][two_path] = temp_options
        # else:
        #     print("ERROR: Could not find a parent or child of PAST path with length 2")
    return mega_dict


def two_long_pathing(signature, mega_dict):
    """ This function changes the paths of length 2 and other similar non-similarities between 2 signatures"""

    # print(f"Pathing with mega_dict: {mega_dict}")

    # Mega dict:
    # - "two_path_parents" contains a list of parent labels for a given path of length 2
    # - "two_path_children" contains a list of children labels for a given path of length 2
    # - "network_starts" and "network_ends" contain lists of parent labels for a given start node
    # - "tree_starts" contains a tuple of child labels for a given start node
    # - "tree_ends" contains a parent label for a given start node

    found_parent_path_dict = {}  # {s1_two_path : (s2_parent, s2_child)}
    found_child_path_dict = {}  # {s1_two_path : (s2_parent, s2_child)}

    found_parent_path_list = []

    # Try changing the 2-long paths in the other signature
    # Checking to find parents of two-long paths
    for two_path in mega_dict["two_path_parents"]:
        for iso_label in mega_dict["two_path_parents"][two_path]:
            signature_parent = signature.inverse_iso_labelling[iso_label]

            # Make a list such that the edges can be changed while iterating
            temp_children = tuple(signature.network.successors(signature_parent))
            temp_found_tuple_list = []
            for signature_child in temp_children:
                # print("Found path")
                temp_found_tuple_list.append((signature_parent, signature_child))
            if temp_found_tuple_list:
                found_parent_path_dict[two_path] = temp_found_tuple_list

    # Checking to find children of two-long paths
    for two_path in mega_dict["two_path_children"]:
        for iso_label in mega_dict["two_path_children"][two_path]:
            signature_child = signature.inverse_iso_labelling[iso_label]

            # Make a list such that the edges can be changed while iterating
            temp_parents = tuple(signature.network.predecessors(signature_child))
            temp_found_tuple_list = []
            for signature_parent in temp_parents:
                # print("Found path")
                temp_found_tuple_list.append((signature_parent, signature_child))
            if temp_found_tuple_list:
                found_child_path_dict[two_path] = temp_found_tuple_list

    # print(f"found_parent_path_dict = {found_parent_path_dict}")
    # print(f"found_child_path_dict = {found_child_path_dict}")

    # Change the paths of length 2 that were found
    output_list = [signature]
    for key in found_parent_path_dict:
        temp_output_list = []
        for old_signature in output_list:
            for item_tuple in found_parent_path_dict[key]:
                new_signature = old_signature.signature_copy()

                signature_parent = item_tuple[0]
                signature_child = item_tuple[1]

                # Check if this edge was already de-compacted in a previous step:
                if (signature_parent, signature_child) not in new_signature.network.edges():
                    # print("Edge already used")
                    continue

                # Lengthen the path in signature by adding a node in between
                new_node = new_signature.node_count + 1
                new_signature.node_count += 1
                new_signature.iso_labelling[new_node] = "FUTURE"
                new_signature.network.add_edge(signature_parent, new_node)
                new_signature.network.add_edge(new_node, signature_child)
                new_signature.network.remove_edge(signature_parent, signature_child)

                # Creating new path if needed
                if (signature_parent, signature_child) in new_signature.embedding.inverse_edge_dict:
                    tree_edge = new_signature.embedding.inverse_edge_dict[(signature_parent, signature_child)]
                    network_path = new_signature.embedding.edge_dict[tree_edge]
                    new_path = []

                    for path_edge in network_path:
                        if path_edge == (signature_parent, signature_child):
                            new_path.append((signature_parent, new_node))
                            new_path.append((new_node, signature_child))
                        else:
                            new_path.append(path_edge)
                    # print(f"New path: {new_path}")

                    # Fix embedding edges
                    new_signature.embedding.inverse_edge_dict[(signature_parent, new_node)] = tree_edge
                    new_signature.embedding.inverse_edge_dict[(new_node, signature_child)] = tree_edge
                    new_signature.embedding.inverse_edge_dict.pop((signature_parent, signature_child))
                    new_signature.embedding.edge_dict[tree_edge] = new_path
                temp_output_list.append(new_signature)
        output_list = temp_output_list

    for key in found_child_path_dict:
        temp_output_list = []
        for old_signature in output_list:
            for item_tuple in found_child_path_dict[key]:

                signature_parent = item_tuple[0]
                signature_child = item_tuple[1]

                # Abort if the edge is already removed
                if (signature_parent, signature_child) not in old_signature.network.edges():
                    continue

                new_signature = old_signature.signature_copy()

                # Lengthen the path in signature by adding a node in between
                new_node = new_signature.node_count + 1
                new_signature.node_count += 1
                new_signature.iso_labelling[new_node] = "FUTURE"
                new_signature.network.add_edge(signature_parent, new_node)
                new_signature.network.add_edge(new_node, signature_child)
                new_signature.network.remove_edge(signature_parent, signature_child)

                # Creating new path if needed
                if (signature_parent, signature_child) in new_signature.embedding.inverse_edge_dict:
                    tree_edge = new_signature.embedding.inverse_edge_dict[
                        (signature_parent, signature_child)]
                    network_path = new_signature.embedding.edge_dict[tree_edge]
                    new_path = []

                    for path_edge in network_path:
                        if path_edge == (signature_parent, signature_child):
                            new_path.append((signature_parent, new_node))
                            new_path.append((new_node, signature_child))
                        else:
                            new_path.append(path_edge)
                    # print(f"New path: {new_path}")

                    # Fix embedding edges
                    new_signature.embedding.inverse_edge_dict[(signature_parent, new_node)] = tree_edge
                    new_signature.embedding.inverse_edge_dict[(new_node, signature_child)] = tree_edge
                    new_signature.embedding.inverse_edge_dict.pop((signature_parent, signature_child))
                    new_signature.embedding.edge_dict[tree_edge] = new_path

                temp_output_list.append(new_signature)
        output_list = temp_output_list

    # Tree starts
    for key in mega_dict["tree_starts"]:
        temp_output_list = []
        for old_signature in output_list:
            new_signature = old_signature.signature_copy()
            node_labels = mega_dict["tree_starts"][key]
            for parent in signature.tree.predecessors(signature.inverse_iso_labelling[node_labels[0]]):
                # Disregard the wrong parent if we have proof against it
                if len(node_labels) > 1:
                    if list(signature.tree.successors(parent)) != node_labels:
                        continue
                if new_signature.iso_labelling[parent] == "FUTURE":
                    if new_signature.tree.in_degree(parent) == 0:

                        # Add node to signature
                        new_node = new_signature.node_count + 1
                        new_signature.node_count += 1
                        new_signature.iso_labelling[new_node] = "FUTURE"
                        new_signature.tree.add_edge(new_node, parent)

                        new_embedding_node = new_signature.node_count + 1
                        new_signature.node_count += 1
                        new_signature.iso_labelling[new_embedding_node] = "FUTURE"
                        new_signature.network.add_edge(new_embedding_node, new_signature.embedding.node_dict[parent])

                        new_signature.embedding.node_dict[new_node] = new_embedding_node
                        new_signature.embedding.inverse_node_dict[new_embedding_node] = new_node

                        new_signature.embedding.edge_dict[(new_node, parent)] = [(new_embedding_node, new_signature.embedding.node_dict[parent])]
                        new_signature.embedding.inverse_edge_dict[(new_embedding_node, new_signature.embedding.node_dict[parent])] = (new_node, parent)

                temp_output_list.append(new_signature)
        output_list = temp_output_list

    # Network starts
    for key in mega_dict["network_starts"]:
        # print(f"Trying key {key} for network starts")
        temp_output_list = []
        for old_signature in output_list:
            new_signature = old_signature.signature_copy()
            node_labels = mega_dict["network_starts"][key]
            # print(f"node_labels = {node_labels}")
            for parent in signature.network.predecessors(signature.inverse_iso_labelling[node_labels[0]]):
                # Disregard the wrong parent if we have proof against it
                # print(f"parent = {parent}")
                if len(node_labels) > 1:
                    test_set = set()
                    for test_child in signature.network.successors(parent):
                        test_set.add(signature.iso_labelling[test_child])

                    if test_set != set(node_labels):
                        continue
                if new_signature.iso_labelling[parent] == "FUTURE":
                    if new_signature.network.in_degree(parent) == 0:
                        if parent in new_signature.embedding.inverse_node_dict:
                            # print("Found network start")

                            # Add node to signature
                            new_node = new_signature.node_count + 1
                            new_signature.node_count += 1
                            new_signature.iso_labelling[new_node] = "FUTURE"
                            new_signature.network.add_edge(new_node, parent)

                            new_embedded_node = new_signature.node_count + 1
                            new_signature.node_count += 1
                            new_signature.iso_labelling[new_embedded_node] = "FUTURE"
                            new_signature.tree.add_edge(new_embedded_node, new_signature.embedding.inverse_node_dict[parent])

                            new_signature.embedding.node_dict[new_embedded_node] = new_node
                            new_signature.embedding.inverse_node_dict[new_node] = new_embedded_node

                            new_signature.embedding.edge_dict[(new_embedded_node, new_signature.embedding.inverse_node_dict[parent])] = [(new_node, parent)]
                            new_signature.embedding.inverse_edge_dict[(new_node, parent)] = (new_embedded_node, new_signature.embedding.inverse_node_dict[parent])

                temp_output_list.append(new_signature)
        output_list = temp_output_list

    return output_list


def signature_joiner(signature1, signature2):
    # print("Trying to join signatures")

    # mapping = NetworkIsomorphismTools.isomorphism_checker7(signature1, signature2)
    mapping = NetworkIsomorphismTools.isomorphism_checker6(signature1, signature2)

    if mapping is False:
        # print("No mapping found")
        return False

    new_signature = signature2.signature_copy()

    # Color nodes
    for node in signature1.iso_labelling:
        if signature1.iso_labelling[node] == "PAST":
            change_node = mapping[node]

            z_in_tree = change_node in new_signature.tree
            found_node = None

            if new_signature.iso_labelling[change_node] != "PAST":
                found_node = change_node
                new_signature.iso_labelling[change_node] = "PAST"
            # Try sibling nodes
            else:
                if z_in_tree:
                    used_graph = new_signature.tree
                else:
                    used_graph = new_signature.network
                # Search through parents
                for parent in used_graph.predecessors(change_node):
                    for sibling in used_graph.successors(parent):
                        if sibling == change_node:
                            continue
                        if set(used_graph.predecessors(sibling)) == set(used_graph.predecessors(change_node)):
                            # Slightly different check for leaves
                            if z_in_tree and change_node in new_signature.network:
                                if sibling in new_signature.network:
                                    if set(new_signature.network.predecessors(sibling)) == set(new_signature.network.predecessors(change_node)):
                                        if new_signature.iso_labelling[sibling] != "PAST":
                                            new_signature.iso_labelling[sibling] = "PAST"
                                            found_node = sibling
                            # Normal check for non-leaves
                            else:
                                if set(used_graph.successors(sibling)) == set(used_graph.successors(change_node)):
                                    if new_signature.iso_labelling[sibling] != "PAST":
                                        found_node = sibling

            if found_node is None:
                print("ERROR: did not find node")
                # TODO: maybe try seeing if we can force a different mapping to some other node.
            else:
                new_signature.iso_labelling[found_node] = "PAST"
                TreeContainment.local_redundancy_check(new_signature, found_node, z_in_tree, "PAST")


    return new_signature


def signature_joiner2(signature1, signature2, sub_signature1, sub_signature2):
    # print("Trying to join signatures")

    # sub_signature1 = signature1.signature_copy()
    # sub_signature2 = signature2.signature_copy()

    # past_to_future_restriction(sub_signature1)
    # past_to_future_restriction(sub_signature2)

    mapping = NetworkIsomorphismTools.isomorphism_checker7(sub_signature1, sub_signature2)
    if mapping is False:
        # print("No mapping found")
        return False

    new_signature = signature2.signature_copy()  # Use signature2, because that works better with the mapping dict

    # ADDING STUFF THAT WAS REMOVED FROM SIGNATURE1
    # 1. Add iso-labellings (and inverse iso-labellings) while updating the mapping
    for node in signature1.tree.nodes():
        if node not in sub_signature1.tree.nodes():
            new_signature.node_count += 1
            mapping[node] = new_signature.node_count
            # Add iso-labellings
            new_signature.iso_labelling[new_signature.node_count] = signature1.iso_labelling[node]
            if signature1.iso_labelling[node] != "FUTURE" and signature1.iso_labelling[node] != "PAST":
                new_signature.inverse_iso_labelling[signature1.iso_labelling[node]] = new_signature.node_count

    for node in signature1.network.nodes():
        if node in signature1.tree:
            continue
        if node not in sub_signature1.network.nodes():
            new_signature.node_count += 1
            mapping[node] = new_signature.node_count
            new_signature.iso_labelling[new_signature.node_count] = signature1.iso_labelling[node]
            if signature1.iso_labelling[node] != "FUTURE" and signature1.iso_labelling[node] != "PAST":
                new_signature.inverse_iso_labelling[signature1.iso_labelling[node]] = new_signature.node_count

    # 2. Add edges in the network
    for edge in signature1.network.edges():
        if edge not in sub_signature1.network.edges():
            new_signature.network.add_edge(mapping[edge[0]], mapping[edge[1]])

    # 3. Add edges and their embeddings in the tree
    for edge in signature1.tree.edges():
        if edge not in sub_signature1.tree.edges():
            new_signature.tree.add_edge(mapping[edge[0]], mapping[edge[1]])
            mapped_path = [(mapping[e[0]], mapping[e[1]]) for e in signature1.embedding.edge_dict[edge]]
            new_signature.embedding.edge_dict[(mapping[edge[0]], mapping[edge[1]])] = mapped_path
            for path_edge in mapped_path:
                new_signature.embedding.inverse_edge_dict[path_edge] = (mapping[edge[0]], mapping[edge[1]])

    # 4. Add embeddings for nodes
    for node in signature1.tree.nodes():
        if node in sub_signature1.tree.nodes():
            continue
        mapped_node = mapping[node]
        mapped_embedding_node = mapping[signature1.embedding.node_dict[node]]
        new_signature.embedding.node_dict[mapped_node] = mapped_embedding_node
        new_signature.embedding.inverse_node_dict[mapped_embedding_node] = mapped_node

    # Color nodes
    changed_nodes = []
    for node in signature1.iso_labelling:
        if signature1.iso_labelling[node] == "PAST":
            change_node = mapping[node]

            z_in_tree = change_node in new_signature.tree
            found_node = None

            if new_signature.iso_labelling[change_node] != "PAST":
                found_node = change_node
            # Detective work when the mapping doesn't correctly handle the iso-labelling
            # Try sibling nodes
            else:
                if z_in_tree:
                    used_graph = new_signature.tree
                else:
                    used_graph = new_signature.network
                # Search through parents
                for parent in used_graph.predecessors(change_node):
                    for sibling in used_graph.successors(parent):
                        if sibling == change_node:
                            continue
                        if set(used_graph.predecessors(sibling)) == set(used_graph.predecessors(change_node)):
                            # Slightly different check for leaves
                            if z_in_tree and change_node in new_signature.network:
                                if sibling in new_signature.network:
                                    if set(new_signature.network.predecessors(sibling)) == set(new_signature.network.predecessors(change_node)):
                                        if new_signature.iso_labelling[sibling] != "PAST":
                                            new_signature.iso_labelling[sibling] = "PAST"
                                            found_node = sibling
                            # Normal check for non-leaves
                            else:
                                if set(used_graph.successors(sibling)) == set(used_graph.successors(change_node)):
                                    if new_signature.iso_labelling[sibling] != "PAST":
                                        found_node = sibling

            if found_node is None:
                print("ERROR: did not find node")
                # TODO: maybe try seeing if we can force a different mapping to some other node.
            else:
                new_signature.iso_labelling[found_node] = "PAST"
                changed_nodes.append(found_node)

    for node in changed_nodes:
        z_in_tree = node in new_signature.tree
        TreeContainment.local_redundancy_check(new_signature, node, z_in_tree, "PAST")

    return new_signature


def past_to_future_restriction(signature):
    # Tree
    before_nodes = tuple(signature.tree.nodes())  # To prevent the dictionary from changing sizes mid-loop
    for node in before_nodes:
        if node not in signature.tree.nodes():
            continue
        if signature.iso_labelling[node] == "PAST":
            signature.iso_labelling[node] = "FUTURE"
            z_in_tree = node in signature.tree
            future_local_redundancy_check(signature, node, z_in_tree, "FUTURE")
    # Network
    before_nodes = tuple(signature.network.nodes())
    for node in before_nodes:
        if node not in signature.network.nodes():
            continue
        if node in signature.tree:
            continue
        if signature.iso_labelling[node] == "PAST":
            signature.iso_labelling[node] = "FUTURE"
            z_in_tree = node in signature.tree
            future_local_redundancy_check(signature, node, z_in_tree, "FUTURE")

    return


def future_local_redundancy_check(signature, used_node, z_in_tree, iso_label):
    """Method function that changes the signature based on redundancy of PAST nodes."""

    # print(f"Local redundancy check (used_node = {used_node})")

    redundant_tree_edges = []   # TODO: This should probably be a set, to prevent duplicates
    redundant_network_edges = []
    part_of_embedding = True  # Assume its true unless it's not
    redundant_tree_nodes = set()
    redundant_network_nodes = set()
    possible_compact_nodes = []

    actual_node = used_node

    if not z_in_tree:
        # Find the inverse embedded node.
        part_of_embedding = used_node in signature.embedding.inverse_node_dict
        if part_of_embedding:
            used_node = signature.embedding.inverse_node_dict[used_node]

    if part_of_embedding:
        # Definition part 1 (tree arcs)
        iterate_tree_edges = list(itertools.chain(signature.tree.in_edges(used_node), signature.tree.out_edges(used_node)))
        for edge in iterate_tree_edges:  # This iterates through both in/out
            if signature.iso_labelling[edge[0]] == iso_label and signature.iso_labelling[edge[1]] == iso_label:
                # Check if all nodes in the network path embedding have the redundant_label
                if all(signature.iso_labelling[node] == iso_label for network_edge in
                       signature.embedding.edge_dict[edge] for node in network_edge):
                    redundant_tree_edges.append(edge)

                    # Definition part 2 (network arcs)
                    iterate_network_edges = signature.embedding.edge_dict[edge].copy()
                    for network_edge in iterate_network_edges:
                        # Remove network edge
                        signature.network.remove_edge(network_edge[0], network_edge[1])
                        signature.embedding.inverse_edge_dict.pop(network_edge)
                        redundant_network_edges.append(network_edge)

                    # Remove tree edge
                    signature.tree.remove_edge(edge[0], edge[1])
                    signature.embedding.edge_dict.pop(edge)
                    redundant_network_edges.append(network_edge)

    else:  # If z is not part of the embedding:

        # Definition part 1 (tree arcs)
        iterate_network_edges = list(itertools.chain(signature.network.in_edges(used_node), signature.network.out_edges(used_node)))
        for edge in iterate_network_edges:
            if edge in signature.embedding.inverse_edge_dict:
                # Check if the embedded tree edges have the same label on both ends
                tree_edge = signature.embedding.inverse_edge_dict[edge]
                if signature.iso_labelling[tree_edge[0]] == iso_label and signature.iso_labelling[tree_edge[1]] == iso_label:
                    # Check if all edges in the embeddings of these tree edges have the redundant_label
                    if all(signature.iso_labelling[node] == iso_label for network_edge in signature.embedding.edge_dict[tree_edge] for node in network_edge):
                        redundant_tree_edges.append(tree_edge)

                        # Definition part 2 (network arcs)
                        # Remove tree edge (and its embeddings)
                        signature.tree.remove_edge(tree_edge[0], tree_edge[1])
                        for network_edge in signature.embedding.edge_dict[tree_edge]:
                            # Remove network edge
                            signature.network.remove_edge(network_edge[0], network_edge[1])  # TODO: new, test this
                            redundant_network_edges.append(network_edge)
                            signature.embedding.inverse_edge_dict.pop(network_edge)
                        signature.embedding.edge_dict.pop(tree_edge)

            # Making sure the network edges that are not part of the embedding are also checked
            else:
                if signature.iso_labelling[edge[0]] == signature.iso_labelling[edge[1]]:
                    # Check if it's not already removed when the tree node was removed
                    if edge in signature.network.edges():
                        # Remove the network edge (not part of embedding)
                        signature.network.remove_edge(edge[0], edge[1])
                        redundant_network_edges.append(edge)

    # Definition part 3 (tree nodes)
    for check_edge in redundant_tree_edges:
        for node in check_edge:
            # Since it is adjacent to a redundant edge, it must have iso-label PAST.
            # Check if all edges are removed
            if signature.tree.in_degree(node) + signature.tree.out_degree(node) == 0:
                # Check if its a leaf
                if node in signature.network:
                    # Check if it also has no neighbors in the network
                    if signature.network.in_degree(node) == 0:
                        redundant_tree_nodes.add(node)

                else:
                    # Check if the embedding node is also redundant
                    embedding_node = signature.embedding.node_dict[node]
                    if signature.iso_labelling[embedding_node] == iso_label:
                        if signature.network.in_degree(embedding_node) + signature.network.out_degree(embedding_node) == 0:
                            redundant_tree_nodes.add(node)

                            # Definition part 4 (network nodes)
                            # Don't need checks for nodes in the embedding since that's already done at part 3
                            if embedding_node not in redundant_network_nodes:
                                redundant_network_nodes.add(embedding_node)

    # Doing the checks for nodes that are not in the embedding:
    for check_edge in redundant_network_edges:
        for node in check_edge:
            # Check if its not a leaf
            if node not in signature.tree:
                if node not in redundant_network_nodes:
                    if node not in signature.embedding.inverse_node_dict:
                        # Check if the node is redundant
                        if signature.network.in_degree(node) + signature.network.out_degree(node) == 0:
                            redundant_network_nodes.add(node)
                        else:
                            if signature.network.in_degree(node) == 1 and signature.network.out_degree(node) == 1:
                                possible_compact_nodes.append(node)
                    # Weird edge case: [Tree nodes edges were removed, but not itself because embedding was not PAST yet]
                    else:
                        embedded_tree_node = signature.embedding.inverse_node_dict[node]
                        # Check if both nodes have no edges
                        if signature.tree.in_degree(embedded_tree_node) + signature.tree.out_degree(embedded_tree_node) == 0:
                            if signature.network.in_degree(node) + signature.network.out_degree(node) == 0:
                                redundant_network_nodes.add(node)
                                redundant_tree_nodes.add(embedded_tree_node)

    # Removing redundant nodes
    for node in redundant_tree_nodes:
        signature.remove(node)
    for node in redundant_network_nodes:
        signature.remove(node)

    # Add neighbors of z to possible compact nodes (since we check whether those neighbors are PAST)
    if not z_in_tree:
        # Check if there's any edges at all
        if signature.network.edges():
            # Check if the node was not already removed
            if actual_node in signature.network:
                for node in itertools.chain(signature.network.predecessors(actual_node), signature.network.successors(actual_node)):
                    if signature.iso_labelling[node] == iso_label:
                        if signature.network.in_degree(node) == 1 and signature.network.out_degree(node) == 1:
                            if node not in signature.embedding.inverse_node_dict:
                                possible_compact_nodes.append(node)

    # Compacting nodes
    for node in possible_compact_nodes:
        for parent in signature.network.predecessors(node):  # Only 1
            if signature.iso_labelling[parent] == iso_label:
                for child in signature.network.successors(node):  # Only 1
                    if signature.iso_labelling[child] == iso_label:
                        # print(f"Compacting node: {node}")

                        signature.network.add_edge(parent, child)
                        # Fix any possible embedding path
                        if (parent, node) in signature.embedding.inverse_edge_dict:
                            embedded_edge = signature.embedding.inverse_edge_dict[(parent, node)]
                            embedding_path = signature.embedding.edge_dict[embedded_edge]
                            # print(f"Old path: {embedding_path}")
                            new_path = []
                            # Remove all edges with the node and insert (parent, child)
                            for path_edge in embedding_path:
                                if path_edge[0] == node:
                                    continue
                                if path_edge[1] == node:
                                    new_path.append((parent, child))
                                else:
                                    new_path.append(path_edge)
                            # print(f"New path: {new_path}")

                            # Fix embedded edge and inverse embedding edge
                            signature.embedding.edge_dict[embedded_edge] = new_path
                            # 1. Remove old inverse embeddings
                            for path_edge in embedding_path:
                                signature.embedding.inverse_edge_dict.pop(path_edge)
                            # 2. Create new inverse embeddings
                            for path_edge in new_path:
                                signature.embedding.inverse_edge_dict[path_edge] = embedded_edge
                        signature.network.remove_node(node)
                        signature.iso_labelling.pop(node)

    return
