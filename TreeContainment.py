import networkx as nx
import itertools
import TreeDecomposition
import TreeContainmentTools
import NetworkIsomorphismTools
import copy  # TODO I don't like this
import random
import TreeContainmentChecks
import IntroduceNode
import JoinNode
random.seed(10)

# ======================================================================================================================
# CLASSES
# ======================================================================================================================


class Embedding:
    def __init__(self, a=None, b=None, c=None, d=None):
        if a is None:
            a = {}
        if b is None:
            b = {}
        if c is None:
            c = {}
        if d is None:
            d = {}

        self.node_dict = a
        self.edge_dict = b
        self.inverse_node_dict = c
        self.inverse_edge_dict = d

    def get_data(self):
        print(f'Node dict: {self.node_dict}')
        print(f'Edge dict: {self.edge_dict}')
        print(f'Inverse node dict: {self.node_dict}')
        print(f'Inverse edge dict: {self.edge_dict}')

    def get_fancy_data(self):
        print()
        print("================================================")
        print("EMBEDDING")
        print("Nodes:")
        for node in self.node_dict:
            print(f"{node} -> {self.node_dict[node]}")
        print("Edges:")
        for node in self.edge_dict:
            print(f"{node} -> {self.edge_dict[node]}")
        print("================================================")


class Signature:
    def __init__(self, a1=None, a2=None, a3=None, a4=None, a5=None, a6=None):
        if a1 is None:
            a1 = nx.DiGraph([])
        if a2 is None:
            a2 = nx.DiGraph([])
        if a3 is None:
            a3 = Embedding({})
        if a4 is None:
            a4 = {}
        if a5 is None:
            a5 = {}
        if a6 is None:
            a6 = 0

        self.tree = a1
        self.network = a2
        self.embedding = a3
        self.iso_labelling = a4
        self.inverse_iso_labelling = a5
        self.node_count = a6

    def iso_label(self, node, label):
        # WARNING: This function is made to be called ONLY for the algorithm. If a node gets the label "PAST", that
        # means it previously had an inverse labelling that should be removed.

        if label == "PAST":
            self.inverse_iso_labelling.pop(self.iso_labelling[node])
        elif label != "FUTURE":
            self.inverse_iso_labelling[label] = node
        self.iso_labelling[node] = label

    def decompact(self, edge):
        # Generate new node
        new_node = self.node_count + 1
        self.node_count += 1

        # Replace edge with 2 edges
        self.network.add_edge(edge[0], new_node)
        self.network.add_edge(new_node, edge[1])
        self.network.remove_edge(edge[0], edge[1])

        # Replace possible embedding
        if edge in self.embedding.inverse_edge_dict:
            embedding_tree_edge = self.embedding.inverse_edge_dict[edge]
            first_part = []
            second_part = []
            passed_the_edge = False
            for path_edge in self.embedding.edge_dict[embedding_tree_edge]:
                if path_edge == edge:
                    passed_the_edge = True
                elif passed_the_edge:
                    second_part.append(path_edge)
                else:
                    first_part.append(path_edge)
            self.embedding.edge_dict[embedding_tree_edge] = first_part + [(edge[0], new_node),
                                                                          (new_node, edge[1])] + second_part
            self.embedding.inverse_edge_dict.pop(edge)
            self.embedding.inverse_edge_dict[(edge[0], new_node)] = embedding_tree_edge
            self.embedding.inverse_edge_dict[(new_node, edge[1])] = embedding_tree_edge

        return new_node

    def remove(self, node):
        # WARNING: This function is made to be called ONLY for redundant nodes (with an isolabelling "PAST")
        # Removing nodes in other situations requires also removing inverse isolabelling!

        # Tree nodes:
        if node in self.tree:  # O(1) lookup
            # Remove the node and in/out arcs from the embedding
            self.embedding.inverse_node_dict.pop(self.embedding.node_dict[node])
            self.embedding.node_dict.pop(node)

            # Remove the embedding
            for edge in itertools.chain(self.tree.in_edges(node), self.tree.out_edges(node)):
                for path_edge in self.embedding.edge_dict[edge]:
                    self.embedding.inverse_edge_dict.pop(path_edge)
                self.embedding.edge_dict.pop(edge)

            # Remove the node (and edges automatically) from the tree
            self.tree.remove_node(node)
            # Remove the node from the isolabelling (don't need inverse since it's "PAST")
            self.iso_labelling.pop(node)
            # Check if the node is a leaf, and remove it from network if necessary
            if node in self.network:
                self.network.remove_node(node)

        # Network nodes
        else:
            # Remove node and in/out arcs from the embedding
            for parent in self.network.predecessors(node):
                edge = (parent, node)
                if edge in self.embedding.inverse_edge_dict:
                    tree_edge = self.embedding.inverse_edge_dict[edge]
                    self.embedding.edge_dict.pop(tree_edge)
                    self.embedding.inverse_edge_dict.pop(edge)
            for child in self.network.successors(node):
                edge = (node, child)
                if edge in self.embedding.inverse_edge_dict:
                    tree_edge = self.embedding.inverse_edge_dict[edge]
                    self.embedding.edge_dict.pop(tree_edge)
                    self.embedding.inverse_edge_dict.pop(edge)

            # for edge in itertools.chain(self.network.in_edges(node), self.network.out_edges(node)):
            #     if edge in self.embedding.inverse_edge_dict:
            #         tree_edge = self.embedding.inverse_edge_dict[edge]
            #         self.embedding.edge_dict.pop(tree_edge)
            #         self.embedding.inverse_edge_dict.pop(edge)

            if node in self.embedding.inverse_node_dict:
                self.embedding.node_dict.pop(self.embedding.inverse_node_dict[node])
                self.embedding.inverse_node_dict.pop(node)

            # Remove the node (and edges automatically) from the tree
            self.network.remove_node(node)
            # Remove the node from the isolabelling (don't need inverse since it's "PAST")
            self.iso_labelling.pop(node)

    def print_iso_labelling(self):
        print(f'iso_labelling: {self.iso_labelling}')
        print(f'inverse_iso_labelling: {self.inverse_iso_labelling}')

    def fancy_iso_labelling(self):
        print()
        print("================================================")
        print("ISO_LABELLING")
        for node in self.iso_labelling:
            print(f"{node} -> {self.iso_labelling[node]}")
        print("INVERSE_ISO_LABELLING:")
        for node in self.inverse_iso_labelling:
            print(f"{node} -> {self.inverse_iso_labelling[node]}")
        print("================================================")

    def print(self, count=0):
        print(f"    [{count}]==============================================[{count}]")
        print(f"    ||TREE NODES: {self.tree.nodes()}")
        print(f"    ||NETWORK NODES: {self.network.nodes()}")
        print(f"    ||TREE EDGES: {self.tree.edges()}")
        # print(f"    ||NETWORK EDGES: {self.network.edges()}")
        temp_edges = list(self.network.edges())
        temp_edges.sort()
        print(f"    ||NETWORK EDGES: {temp_edges}")
        print(f"    ||EMBEDDING NODES: {self.embedding.node_dict}")
        print(f"    ||INVERSE EMBEDDING NODES: {self.embedding.inverse_node_dict}")
        print(f"    ||EMBEDDING EDGES: {self.embedding.edge_dict}")
        print(f"    ||INVERSE EMBEDDING EDGES: {self.embedding.inverse_edge_dict}")
        print(f"    ||ISOLABELLING: {self.iso_labelling}")
        print(f"    ||INVERSE-ISOLABELLING: {self.inverse_iso_labelling}")
        print(f"    ||NODE COUNT (LIMIT): {self.node_count}")
        print(
            f"    ||NODE COUNT (ACTUAL): {self.tree.number_of_nodes() + len([node for node in self.network.nodes() if node not in self.tree.nodes()])}")
        print(f"    [{count}]==============================================[{count}]")

    def signature_copy(self):
        new_embedding = Embedding(self.embedding.node_dict.copy(), copy.deepcopy(self.embedding.edge_dict),  # TODO: ultra slow deepcopy, but necessary somehow!? Maybe try making our own copy that's now deepdeep but still deep. Maybe try using tuples instead of lists for paths?
                                  self.embedding.inverse_node_dict.copy(), copy.deepcopy(self.embedding.inverse_edge_dict))

        return Signature(self.tree.copy(), self.network.copy(), new_embedding, self.iso_labelling.copy(),
                         self.inverse_iso_labelling.copy(), self.node_count)  # TODO: This copying might be slow


# ======================================================================================================================
# ALGORITHM
# ======================================================================================================================


def leaf_node():
    return [Signature()]


def forget_node(signature, node_z):
    # Find out which node is labelled to z
    used_node = signature.inverse_iso_labelling[node_z]
    signature.iso_label(used_node, "PAST")
    z_in_tree = used_node in signature.tree.nodes()  # TODO: Might have a faster way of doing this in the future.
    local_redundancy_check(signature, used_node, z_in_tree, "FUTURE")
    # print("Forget output:")
    # signature.print()
    return signature


def local_redundancy_check(signature, used_node, z_in_tree, iso_label):
    """Method function that changes the signature based on redundancy of PAST nodes."""

    # print(f"\nLocal redundancy check (used_node = {used_node})")

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
            if signature.iso_labelling[edge[0]] == "PAST" and signature.iso_labelling[edge[1]] == "PAST":
                # Check if all nodes in the network path embedding have the redundant_label
                if all(signature.iso_labelling[node] == "PAST" for network_edge in
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
                if signature.iso_labelling[tree_edge[0]] == "PAST" and signature.iso_labelling[tree_edge[1]] == "PAST":
                    # Check if all edges in the embeddings of these tree edges have the redundant_label
                    if all(signature.iso_labelling[node] == "PAST" for network_edge in signature.embedding.edge_dict[tree_edge] for node in network_edge):
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
                    if signature.iso_labelling[embedding_node] == "PAST":
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
                            # Check if the node can be compacted
                            if signature.network.in_degree(node) == 1 and signature.network.out_degree(node) == 1:
                                possible_compact_nodes.append(node)
                    # Weird edge case: [Tree nodes edges were removed, but not itself because embedding was not PAST yet]
                    else:
                        embedded_tree_node = signature.embedding.inverse_node_dict[node]
                        # Check if both nodes have no edges
                        # print(embedded_tree_node)
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
                    if signature.iso_labelling[node] == "PAST":
                        if signature.network.in_degree(node) == 1 and signature.network.out_degree(node) == 1:
                            if node not in signature.embedding.inverse_node_dict:
                                possible_compact_nodes.append(node)

    # Compacting nodes
    for node in possible_compact_nodes:
        for parent in signature.network.predecessors(node):  # Only 1
            if signature.iso_labelling[parent] == "PAST":
                for child in signature.network.successors(node):  # Only 1
                    if signature.iso_labelling[child] == "PAST":
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
                                # if path_edge not in signature.embedding.inverse_edge_dict:
                                    # TreeContainmentTools.signature_image(signature, 99)
                                    # signature.print(99)
                                signature.embedding.inverse_edge_dict.pop(path_edge)
                            # 2. Create new inverse embeddings
                            for path_edge in new_path:
                                signature.embedding.inverse_edge_dict[path_edge] = embedded_edge
                        signature.network.remove_node(node)
                        signature.iso_labelling.pop(node)

    # Compacting nodes
    for node in possible_compact_nodes:
        if node not in signature.network:
            # print(f"node = {node}")
            # TreeContainmentTools.signature_image(signature, 99)
            continue
        for parent in signature.network.predecessors(node):  # Only 1
            if signature.iso_labelling[parent] == "PAST":
                for child in signature.network.successors(node):  # Only 1
                    if signature.iso_labelling[child] == "PAST":
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
                                # if path_edge not in signature.embedding.inverse_edge_dict:
                                    # TreeContainmentTools.signature_image(signature, 99)
                                    # signature.print(99)
                                signature.embedding.inverse_edge_dict.pop(path_edge)
                            # 2. Create new inverse embeddings
                            for path_edge in new_path:
                                signature.embedding.inverse_edge_dict[path_edge] = embedded_edge
                        signature.network.remove_node(node)
                        signature.iso_labelling.pop(node)

    # # Super-compacting nodes #
    # for node in possible_compact_nodes:
    #     for parent in signature.network.predecessors(node):  # Only 1
    #         for child in signature.network.successors(node):  # Only 1
    #             if signature.iso_labelling[parent] == "PAST" or signature.iso_labelling[child] == "PAST":
    #                 # print(f"Compacting node: {node}")
    #
    #                 signature.network.add_edge(parent, child)
    #                 # Fix any possible embedding path
    #                 if (parent, node) in signature.embedding.inverse_edge_dict:
    #                     embedded_edge = signature.embedding.inverse_edge_dict[(parent, node)]
    #                     embedding_path = signature.embedding.edge_dict[embedded_edge]
    #                     # print(f"Old path: {embedding_path}")
    #                     new_path = []
    #                     # Remove all edges with the node and insert (parent, child)
    #                     for path_edge in embedding_path:
    #                         if path_edge[0] == node:
    #                             continue
    #                         if path_edge[1] == node:
    #                             new_path.append((parent, child))
    #                         else:
    #                             new_path.append(path_edge)
    #                     # print(f"New path: {new_path}")
    #
    #                     # Fix embedded edge and inverse embedding edge
    #                     signature.embedding.edge_dict[embedded_edge] = new_path
    #                     # 1. Remove old inverse embeddings
    #                     for path_edge in embedding_path:
    #                         # if path_edge not in signature.embedding.inverse_edge_dict:
    #                             # TreeContainmentTools.signature_image(signature, 99)
    #                             # signature.print(99)
    #                         signature.embedding.inverse_edge_dict.pop(path_edge)
    #                     # 2. Create new inverse embeddings
    #                     for path_edge in new_path:
    #                         signature.embedding.inverse_edge_dict[path_edge] = embedded_edge
    #                 signature.network.remove_node(node)
    #                 signature.iso_labelling.pop(node)

    # print(f"redundant_tree_edges = {redundant_tree_edges}")
    # print(f"redundant_network_edges = {redundant_network_edges}")
    # print(f"redundant_tree_nodes = {redundant_tree_nodes}")
    # print(f"redundant_network_nodes = {redundant_network_nodes}")

    return


def on_the_fly_checking(network_in, tree_in, signature):
    """This procedure function checks a signature to see there are leaves that can be changed "on the fly".
    It returns a list of nodes that it is unsure about"""
    # print()
    # print("On the fly checking signature")
    unsure_nodes = []
    for node in signature.tree.nodes():
        do_not_process = False  # Used to make sure network-side checks are not done in case of tree-side success
        # Check for potential leaves
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
                            not_sure = True
                            continue
                        iso_parent = signature.iso_labelling[parent]

                        # Check parents children in D_IN
                        leaf_list = []
                        for potential_child in tree_in.successors(iso_parent):
                            if potential_child in network_in:
                                leaf_list.append(potential_child)

                        # Stop if there's no leaves at all
                        if not leaf_list:
                            do_not_process = True  # TODO: this is new
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
            signature.embedding.inverse_edge_dict.pop(removed_edge)
            embedding_path.append((network_parent, node))
            signature.embedding.edge_dict[(tree_parent, node)] = embedding_path
            signature.embedding.inverse_edge_dict[(network_parent, node)] = (tree_parent, node)
            signature.embedding.node_dict[node] = node
            signature.embedding.inverse_node_dict[node] = node

    # TODO: consider doing a check here to see if there exists a node in the input display graph with the treeside parent and the networkside parent that the given node has.
    return


# def join_node(network_in, tree_in, bag1, bag2):
#     output_list = []
#
#     mega_mega_dict1 = {}
#     mega_mega_dict2 = {}
#
#     # Creating mega_dicts
#     print(f"Bag 1: {bag1}")
#     for count, signature in enumerate(bag1):
#         mega_mega_dict1[count] = join_path_finder(signature)
#         print(f"mega_dict[{count}] = {mega_mega_dict1[count]}")
#         signature.print(1337)
#     print(f"Bag 2: {bag2}")
#     for count, signature in enumerate(bag2):
#         mega_mega_dict2[count] = join_path_finder(signature)
#         print(f"mega_dict[{count}] = {mega_mega_dict2[count]}")
#         signature.print(1337)
#
#     # Keep track of which signatures already passed the join node
#     done_signature_set_1 = set()
#     done_signature_set_2 = set()
#
#     for count1, signature1 in enumerate(bag1):
#         for count2, signature2 in enumerate(bag2):
#             # if count1 in done_signature_set_1:
#             #     break
#             # if count2 in done_signature_set_2:
#             #     continue
#
#             new_signature1 = signature1.signature_copy()
#             new_signature2 = signature2.signature_copy()
#
#             print(f"\nTRYING SIGNATURES {count1} AND {count2}:")
#
#             # Do the two_path changing in both directions
#             signature_list1 = two_long_pathing(new_signature1, mega_mega_dict2[count2])
#             signature_list2 = two_long_pathing(new_signature2, mega_mega_dict1[count1])
#
#             # Try every signature of the outcome
#             for new_new_signature1 in signature_list1:
#                 for new_new_signature2 in signature_list2:
#
#                     unsure_node_list_1 = on_the_fly_checking(network_in, tree_in, new_new_signature1)
#                     unsure_node_list_2 = on_the_fly_checking(network_in, tree_in, new_new_signature2)
#
#                     # TODO: try finding some more intelligent way of doing this?
#                     # Try every option
#                     try_list_1 = [new_new_signature1]
#                     try_list_2 = [new_new_signature2]
#
#                     for node in unsure_node_list_1:
#                         max_iteration = len(try_list_1)
#                         for i in range(max_iteration):
#                             new_signature = try_list_1[i].signature_copy()
#                             on_the_fly_changing(node, new_signature)
#                             try_list_1.append(new_signature)
#
#                     for node in unsure_node_list_2:
#                         max_iteration = len(try_list_2)
#                         for i in range(max_iteration):
#                             new_signature = try_list_2[i].signature_copy()
#                             on_the_fly_changing(node, new_signature)
#                             try_list_2.append(new_signature)
#
#                     print(f"unsure_node_list_1: {unsure_node_list_1}")
#                     print(f"unsure_node_list_2: {unsure_node_list_2}")
#
#                     success = False
#                     for try_signature_1 in try_list_1:
#                         for try_signature_2 in try_list_2:
#                             temp_output = signature_joiner(try_signature_1, try_signature_2)
#                             if temp_output is not False:
#                                 output_list.append(temp_output)
#                                 done_signature_set_1.add(count1)
#                                 done_signature_set_2.add(count2)
#                                 success = True
#                                 break
#                         if success:
#                             break
#
#     # for count, signature in enumerate(output_list):
#     #     TreeContainmentTools.signature_image(signature, count+100)
#
#     return output_list


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
        else:
            print("ERROR: Could not find a parent or child of PAST path with length 2")
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

    mapping = NetworkIsomorphismTools.isomorphism_checker7(signature1, signature2)
    if mapping is False:
        # print("No mapping found")
        return False
    # new_signature = signature1.signature_copy()
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

            # if found_node is None:
                # print("ERROR: did not find node")
                # TODO: maybe try seeing if we can force a different mapping to some other node.
            new_signature.iso_labelling[found_node] = "PAST"
            local_redundancy_check(new_signature, found_node, z_in_tree)

    # print("Result:")
    # new_signature.print(1337)
    # if mapping == {6: 3, 12: 8, 13: 9, 11: 1, 9: 6, 1: 5, 7: 2, 2: 4}:
    # # if mapping == {3: 2, 7: 7, 8: 8, 11: 11, 12: 12, 1: 5, 9: 9, 5: 4, 2: 1, 6: 6, 10: 10, 4: 3}:
    # # if mapping == {3: 2, 7: 7, 8: 8, 11: 11, 9: 9, 1: 5, 12: 12, 5: 4, 2: 1, 6: 6, 10: 10, 4: 3}:
    # # if (7, 12) not in new_signature.network.edges() and (2, 5) not in new_signature.network.edges():
    #     TreeContainmentTools.signature_image(new_signature, 99)
    #     TreeContainmentTools.signature_image(signature1, 101)
    #     TreeContainmentTools.signature_image(signature2, 102)
    #
    #     print("TESTTEST")


        # if change_node in new_signature.tree:
        #     new_signature.iso_labelling[change_node] = "PAST"
        #     local_redundancy_check(new_signature, node, True)
        # if change_node in new_signature.network:
        #     new_signature.iso_labelling[change_node] = "PAST"
        #     local_redundancy_check(new_signature, node, False)
        # else, it has already been removed by a redundancy


    # loop_list = list(new_signature.tree.nodes())
    # loop_list.extend(list(new_signature.network.nodes()))
    # for node in loop_list:
    #     # Check if it hasn't been removed yet
    #     if node in new_signature.tree or node in new_signature.network:
    #         label1 = signature1.iso_labelling[node]
    #         label2 = signature2.iso_labelling[mapping[node]]
    #         if (label1 == "FUTURE" and label2 == "PAST") or (label1 == "PAST" and label2 == "FUTURE"):
    #             new_signature.iso_labelling[node] = "PAST"  # Note: don't use iso_label() here, that's for PRESENT->PAST
    #             z_in_tree = node in new_signature.tree
    #             local_redundancy_check(new_signature, node, z_in_tree)

    return new_signature


def main_algorithm(tree_in, network_in, decomposition):
    """"This function takes a tree and a network with outdegree-1 roots and nodes that have strings as names
    (numbers are untested). It returns whether the tree is contained within the network"""
    # Check if the input is a tree or a path decomposition:

    super_compact = True
    for node in decomposition:
        if decomposition.out_degree(node) == 2:
            super_compact = False

    # print(f"super_compact = {super_compact}")

    # Generate dictionaries
    descendant_in_dict, depth_in_dict = TreeContainmentChecks.descendant_in_dict_generator(network_in, tree_in)
    neighbor_in_dict = TreeContainmentChecks.neighbor_in_dict_generator(tree_in)
    sibling_in_dict = TreeContainmentChecks.sibling_in_dict_generator(network_in)

    # print(f"descendant_in_dict = {descendant_in_dict}")
    # print(f"depth_in_dict = {depth_in_dict}")
    # print(f"neighbor_in_dict = {neighbor_in_dict}")
    # print(f"sibling_dict[parent_side] = ", sibling_in_dict["parent_side"])
    # print(f"sibling_dict[child_side] = ", sibling_in_dict["child_side"])

    signature_dictionary = {}

    # decomposition = TreeDecomposition.nice_tree_decomposition(display_graph)

    leaf_bags = []
    maximum_number_of_nodes = tree_in.number_of_nodes() + network_in.number_of_nodes()

    # Find leaf bags
    for bag in decomposition:
        if decomposition.out_degree(bag) == 0:
            leaf_bags.append(bag)

    for node in leaf_bags:
        signature_dictionary[node] = leaf_node()
    todo_list = []
    for node in leaf_bags:
        todo_list.extend(list(decomposition.predecessors(node)))
    while len(todo_list) > 0:
        # print(f"todo_list: {todo_list}")
        current_bag = todo_list.pop()
        child = list(decomposition.successors(current_bag))[0]
        isomorphism_check = True

        # Introduce_bag
        if len(current_bag[1]) == len(child[1]) + 1:
            introduced_letter = None
            for letter in current_bag[1]:
                if letter not in list(decomposition.successors(current_bag))[0][1]:
                    introduced_letter = letter
            # print(f"\n[!] {current_bag[0]} Introduced node {introduced_letter} by introduce Bag: {current_bag}")
            z_in_tree = introduced_letter in tree_in.nodes()
            signature_dictionary[current_bag] = []
            for count, child_signature in enumerate(signature_dictionary[child]):
                # if child_signature.tree.number_of_nodes() + child_signature.network.number_of_nodes() <= maximum_number_of_nodes + 3:  # TODO: temp change
                    # print("SIGNATURE GOING INTO INTRODUCE BAG:")
                    # child_signature.print()
                    # if introduced_letter != "f":  # This is the stop (stopstop)
                signature_dictionary[current_bag].extend(IntroduceNode.introduce_node(tree_in, network_in, child_signature, introduced_letter, z_in_tree, descendant_in_dict, depth_in_dict, neighbor_in_dict, sibling_in_dict, super_compact))
            todo_list.extend(list(decomposition.predecessors(current_bag)))

        # Forget bag
        elif len(current_bag[1]) == len(child[1]) - 1:
            forgot_letter = None
            for letter in list(decomposition.successors(current_bag))[0][1]:
                if letter not in current_bag[1]:
                    forgot_letter = letter
            # print(f"\n[!] {current_bag[0]} Forgot node     {forgot_letter} by forget bag:    {current_bag}")

            z_in_tree = forgot_letter in tree_in.nodes()
            signature_dictionary[current_bag] = []
            for count, child_signature in enumerate(signature_dictionary[child]):
                if child_signature.tree.number_of_nodes() + child_signature.network.number_of_nodes() <= maximum_number_of_nodes + 3:  # TODO: temp change
                    # print("SIGNATURE GOING INTO FORGET BAG:")
                    # child_signature.print()
                    signature_dictionary[current_bag].append(forget_node(child_signature, forgot_letter))
            todo_list.extend(list(decomposition.predecessors(current_bag)))

        # Join bag
        elif len(current_bag[1]) == len(child[1]):
            # Check if this bag was not already processed (since it gets added twice by its 2 children to the list)
            if current_bag not in signature_dictionary:
                # Check if children bags are ready
                if all(child in signature_dictionary for child in decomposition.successors(current_bag)):
                    # print(f"\n[!] {current_bag[0]} Join bag {current_bag}")
                    children = list(decomposition.successors(current_bag))
                    # print(f"children = {children}")
                    signature_dictionary[current_bag] = JoinNode.join_node(network_in, tree_in, signature_dictionary[children[0]], signature_dictionary[children[1]])
                    todo_list.extend(list(decomposition.predecessors(current_bag)))

                else:
                    # print(f"\n[!] Join bag not yet ready {current_bag}")
                    isomorphism_check = False

        # Isomorphism checking
        if isomorphism_check:  # To prevent checking join bags that are not yet ready
            # print(f"\n ISOMORPHISM CHECKING for {current_bag}")
            # print(f"Number of signatures before isomorphism check: {len(signature_dictionary[current_bag])}")



            remove_signature_set = set()
            for c1, child_signature1 in enumerate(signature_dictionary[current_bag]):
                if child_signature1 in remove_signature_set:
                    continue
                for c2, child_signature2 in enumerate(signature_dictionary[current_bag]):
                    if c1 >= c2:
                        continue
                    if child_signature2 in remove_signature_set:
                        continue

                    if NetworkIsomorphismTools.isomorphism_checker6(child_signature1, child_signature2):
                        remove_signature_set.add(child_signature2)

            for remove_signature in remove_signature_set:
                signature_dictionary[current_bag].remove(remove_signature)

            # print(f"Number of signatures after: {len(signature_dictionary[current_bag])}")

        # Stop if empty
        if current_bag in signature_dictionary:
            if len(signature_dictionary[current_bag]) == 0:
                # print("Empty bag")
                return False

        # Some examples of manual filters for debugging
        #
        # if current_bag[0] == 6:
        #     signature_dictionary[current_bag] = [s for s in signature_dictionary[current_bag] if
        #                                          (3, 10) in s.network.edges() and
        #                                          (3, 9) in s.network.edges() and
        #                                          (6, 8) in s.network.edges() and
        #                                          (6, 7) in s.network.edges()
        #                                          ]
        #
        # if current_bag in signature_dictionary:
        #     remove_set = set()
        #     for s in signature_dictionary[current_bag]:
        #         for node in s.network.nodes():
        #             if node in s.tree:
        #                 continue
        #             if s.iso_labelling[node] in ["g", "f", "rootN"]:
        #                 if node in s.embedding.inverse_node_dict:
        #                     continue
        #             elif s.iso_labelling[node] in ["FUTURE", "PAST"]:
        #                 continue
        #             else:
        #                 if node not in s.embedding.inverse_node_dict:
        #                     continue
        #             remove_set.add(s)
        #
        #     for s in remove_set:
        #         signature_dictionary[current_bag].remove(s)
        #
        # if current_bag[0] == 14:
        #     signature_dictionary[current_bag] = [s for s in signature_dictionary[current_bag] if
        #                                          (
        #                                           s.node_count < 10
        #                                          )]
        #
        # Printing stuff
        # if current_bag[0] == 999:
        #     if current_bag in signature_dictionary:  # Needed to avoid first-time join bag issues
        #         for count, image_signature in enumerate(signature_dictionary[current_bag]):
        #             if count <= 20:
        #                 TreeContainmentTools.signature_image(image_signature, count)
        #             else:
        #                 print("ERROR: TOO MANY SIGNATURES")
        #                 break
        #
        #     # Manual stop
        # if current_bag[0] == 1000:
        #     return False

    # print("\n\n\nDONE\n")
    for bag in decomposition:
        if decomposition.in_degree(bag) == 0:
            # print(f"Final bag is {bag}")
            for signature in signature_dictionary[bag]:
                # signature.print()
                if all(signature.iso_labelling[node] != "FUTURE" for node in signature.iso_labelling):
                    # print("\nSUCCESS!")
                    return True
    return False
