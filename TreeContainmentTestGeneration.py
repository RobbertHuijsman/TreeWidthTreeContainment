import networkx as nx
import time
import os
import random
import math
import TreeDecomposition
# random.seed(10)  # TODO: comment or uncomment this.


def number_to_letters(number):
    """Takes a number and returns a string containing one or more letters based on the alphabet order.
    0 = a, 25 = z, 26 = aa, etc.
    WARNING: Doesn't work well for number > 675"""

    # number = number + 1  # Math purposes
    output_string = ""
    all_letters = "abcdefghijklmnopqrstuvwxyz"
    if number == 0:
        return "a"
    else:
        degree = math.log(number, 26)
    # Round down the number
    degree = math.floor(degree)

    for count in range(degree + 1):
        times_divided = math.floor(number / (26 ** (degree - count)))

        number = number % (26 ** (degree - count))
        # 0 = a, but 26 = aa, not ba etc.
        if count == 0 and degree > 0:
            output_string = output_string + all_letters[times_divided-1]
        else:
            output_string = output_string + all_letters[times_divided]

    return output_string


def letters_to_number(letters):
    number = 0
    for count, letter in enumerate(letters):
        number += (ord(letter) - 96) * 26 ** (len(letters) - 1 - count)
    return number - 1


def make_tree_edges(number_of_leaves):
    node_number = number_of_leaves

    # Setting up the leaf_dict
    leaf_list = []
    for count in range(number_of_leaves):
        leaf = number_to_letters(count)
        leaf_list.append(leaf)

    # Setting up the edge_dict
    edge_list = []
    while len(leaf_list) > 1:
        random_integer = random.randint(0, len(leaf_list)-2)  # we take the pairs in between leaves

        new_element = number_to_letters(node_number)
        node_number += 1
        edge_list.append((new_element, leaf_list[random_integer]))
        edge_list.append((new_element, leaf_list[random_integer + 1]))

        leaf_list[random_integer] = new_element
        leaf_list.pop(random_integer + 1)

    return edge_list


def descendant_search(node, edge_list):
    descendant_set = set()
    todo_list = [node]

    # Continue searching through children
    number_of_tries = 0
    while todo_list:
        number_of_tries += 1
        if number_of_tries > 10000:
            print("Stopped searching for descendants after 10000 iterations")
            return False

        node = todo_list.pop()

        if node in descendant_set:
            continue

        descendant_set.add(node)

        for edge in edge_list:
            if edge[0] == node:
                todo_list.append(edge[1])

    return descendant_set


def make_network_and_tree_edges(number_of_leaves, number_of_reticulations, add_roots):
    # Generate tree edges
    tree_edges = make_tree_edges(number_of_leaves)

    # Trivial case (crashes somehow if not done manually):
    if number_of_leaves == 1:
        network_edges = [("rootN", "a")]
        tree_edges = [("rootT", "a")]
        return network_edges, tree_edges

    if add_roots:
        add_root_node(tree_edges, "rootT")

    # Change labels of tree edges that are not leaves (leaves should have the same labels)
    network_edges = []
    for edge in tree_edges:
        number = letters_to_number(edge[0])
        number += number_of_leaves - 1
        letters = number_to_letters(number)
        edge_0 = letters

        number = letters_to_number(edge[1])

        if number > number_of_leaves - 1:
            number += number_of_leaves - 1
            letters = number_to_letters(number)
            edge_1 = letters
        else:
            edge_1 = edge[1]
        if edge[0] == "rootT":
            edge_0 = "rootN"

        network_edges.append((edge_0, edge_1))

    # Generate the tree node (parent_edge) and the reticulation node (edge)
    node_number = 3 * number_of_leaves - 2  # 1*leaves + 2*(leaves - 1) = 3*leaves - 2
    for count in range(number_of_reticulations):
        number_of_tries = 0
        while True:
            number_of_tries += 1
            if number_of_tries > 1000:
                print("failure (network making)")
                return network_edges
            edge = random.choice(network_edges)
            parent_edge = random.choice(network_edges)
            if descendant_search(edge[0], network_edges) is False:  # TODO: Not sure why this is needed
                return network_edges, tree_edges
            if parent_edge != edge and parent_edge[0] not in descendant_search(edge[0], network_edges):
                break

        # turn edge into a reticulation node
        new_node1 = number_to_letters(node_number)

        node_number += 1
        network_edges.remove(edge)
        network_edges.append((edge[0], new_node1))
        network_edges.append((new_node1, edge[1]))

        # turn parent edge into a tree node node
        new_node2 = number_to_letters(node_number)
        node_number += 1
        network_edges.remove(parent_edge)
        network_edges.append((parent_edge[0], new_node2))
        network_edges.append((new_node2, parent_edge[1]))

        # Connect both new nodes
        network_edges.append((new_node2, new_node1))

    return network_edges, tree_edges


def add_root_node(edge_list, root_name):
    """This method adds a root to an edge list of a graph. It works in-place, and does not return a value."""
    non_root_list = [edge[1] for edge in edge_list]
    root_child = [edge[0] for edge in edge_list if edge[0] not in non_root_list]
    if root_child == []:
        print("Error, no eligible root node found")
        return False
    root_child = root_child[0]
    edge_list.append((root_name, root_child))


def make_files(number_of_files, number_of_leaves, number_of_reticulations, add_roots, folder_name):
    """"Generates a number of .txt files containing lists of edges of networks and trees that are contained in them"""
    try:
        os.mkdir("./" + folder_name + "/")
    except:
        pass
    f = open("./" + folder_name + "/hits_and_misses.txt", "w+")
    f.write("index; success? ; runtime \n")
    f.close()
    start = time.time()

    for file_number in range(number_of_files):
        index = "0000" + str(file_number)
        index = index[-4:]
        print(index)

        network_edges, tree_edges = make_network_and_tree_edges(number_of_leaves, number_of_reticulations, add_roots)

        # Randomize the orders of the edges for scientific integrity!
        random.shuffle(network_edges)
        random.shuffle(tree_edges)

        f = open("./" + folder_name + "/input" + index + ".txt", "w+")
        f.write(str(network_edges) + "\n")
        f.write(str(tree_edges))
        f.close()

    end = time.time()
    print("time elapsed:", end - start, "seconds")


def make_false_files(number_of_files, number_of_leaves, number_of_reticulations, add_roots, folder_name):
    """"Generates a number of .txt files containing lists of edges of networks and trees that are NOT contained in
    them"""
    try:
        os.mkdir("./" + folder_name + "/")
    except:
        pass
    f = open("./" + folder_name + "/hits_and_misses.txt", "w+")
    f.write("index; success? ; runtime \n")
    f.close()
    start = time.time()

    for file_number in range(number_of_files):
        index = "0000" + str(file_number)
        index = index[-4:]
        print(index)

        network_edges, temp = make_network_and_tree_edges(number_of_leaves, number_of_reticulations, add_roots)
        tree_edges = make_tree_edges(number_of_leaves)
        add_root_node(tree_edges, "rootT")

        # Randomize the orders of the edges for scientific integrity!
        random.shuffle(network_edges)
        random.shuffle(tree_edges)

        f = open("./" + folder_name + "/input" + index + ".txt", "w+")
        f.write(str(network_edges) + "\n")
        f.write(str(tree_edges))
        f.close()

    end = time.time()
    print("time elapsed:", end - start, "seconds")
    return


def make_range_of_files(range_max, constant, test_set_type, add_roots, folder_name, truth_variable):
    """"Generates a number of .txt files containing lists of edges of networks and trees that are contained in them,
    unless the truth_variable == False"""
    try:
        os.mkdir("./" + folder_name + "/")
    except:
        pass
    f = open("./" + folder_name + "/hits_and_misses.txt", "w+")
    f.write("index; success? ; runtime \n")
    f.close()
    start = time.time()

    for file_number in range(range_max):
        # if file_number not in [2, 3, 5]:
        #     continue

        index = "0000" + str(file_number)
        index = index[-4:]
        print(index)

        number_of_leaves = 0
        number_of_reticulations = 0

        if test_set_type == "ratio":
            number_of_leaves = file_number + 1  # +1 since the range starts at 0 and ends at max-1
            number_of_reticulations = math.floor(constant * number_of_leaves)
        elif test_set_type == "constant_reticulations":
            number_of_leaves = file_number + 1  # +1 since the range starts at 0 and ends at max-1
            number_of_reticulations = constant
        elif test_set_type == "constant_leaves":
            number_of_leaves = constant
            number_of_reticulations = file_number
        elif test_set_type == "constant_treewidth":
            number_of_leaves = 3
            number_of_reticulations = file_number

        if test_set_type != "constant_treewidth":
            network_edges, tree_edges = make_network_and_tree_edges(number_of_leaves, number_of_reticulations, add_roots)
            generation_success = True
        else:
            treewidth = 0
            tries = 0
            generation_success = True
            # Try 100 times to get a tree decomposition with the right width
            while treewidth != constant:
                if tries > 100:
                    print("Failure")
                    generation_success = False
                    break

                network_edges, tree_edges = make_network_and_tree_edges(number_of_leaves, number_of_reticulations, add_roots)
                tree = nx.DiGraph(tree_edges)
                network = nx.DiGraph(network_edges)
                display_graph = TreeDecomposition.display_graph_generator(tree, network)
                t_decomposition = TreeDecomposition.tree_decomposition(display_graph)
                treewidth = 0
                for node in t_decomposition.nodes():
                    if len(node[1]) > treewidth:
                        treewidth = len(node[1])
                treewidth -= 1
                # print(f"treewidth = {treewidth}")
                tries += 1

        if not truth_variable:
            tree_edges = make_tree_edges(number_of_leaves)
            add_root_node(tree_edges, "rootT")

        # Randomize the orders of the edges for scientific integrity!
        random.shuffle(network_edges)
        random.shuffle(tree_edges)

        if (number_of_leaves > 2 or truth_variable) and generation_success:
            f = open("./" + folder_name + "/input" + index + ".txt", "w+")
            f.write(str(network_edges) + "\n")
            f.write(str(tree_edges))
            f.close()

    end = time.time()
    print("time elapsed:", end - start, "seconds")


# def make_range_of_false_files(number_of_leaves_max, reticulation_percentage, add_roots, folder_name):
#     """"Generates a number of .txt files containing lists of edges of networks and trees that are contained in them"""
#     try:
#         os.mkdir("./" + folder_name + "/")
#     except:
#         pass
#     f = open("./" + folder_name + "/hits_and_misses.txt", "w+")
#     f.write("index; success? ; runtime \n")
#     f.close()
#     start = time.time()
#
#     for file_number in range(number_of_leaves_max):
#         if file_number < 3:
#             # Networks with less than 3 leaves always have a tree embedding!
#             continue
#         index = "0000" + str(file_number)
#         index = index[-4:]
#         print(index)
#
#         number_of_leaves = file_number+1  # +1 since the range starts at 0 and ends at max-1
#         number_of_reticulations = math.floor(reticulation_percentage * number_of_leaves)
#
#         network_edges, temp = make_network_and_tree_edges(number_of_leaves, number_of_reticulations, add_roots)
#         tree_edges = make_tree_edges(number_of_leaves)
#         add_root_node(tree_edges, "rootT")
#
#         # Randomize the orders of the edges for scientific integrity!
#         random.shuffle(network_edges)
#         random.shuffle(tree_edges)
#
#
#         f = open("./" + folder_name + "/input" + index + ".txt", "w+")
#         f.write(str(network_edges) + "\n")
#         f.write(str(tree_edges))
#         f.close()
#
#     end = time.time()
#     print("time elapsed:", end - start, "seconds")


# networkEdges, treeEdges = make_network_and_tree_edges(4, 1, True)
# print(networkEdges)
# add_root_node(networkEdges, "rootN")
# add_root_node(treeEdges, "rootT")
# network = nx.DiGraph(networkEdges)
# tree = nx.DiGraph(treeEdges)
# TreeDecomposition.display_graph_image(tree, network)


# numberOfFiles = 1
# numberOfLeaves = 28
# numberOfReticulation = 14
# addRoots = True
# folderName = "TestSetTEST"
#
# make_files(numberOfFiles, numberOfLeaves, numberOfReticulation, addRoots, folderName)

truth_variable = True
range_max = 20
addRoots = True
folderName = "TestSet3ConstantTreewidth_True_3"
constant = 3
# test_set_type in ["constant_reticulations", "constant_treewidth", "constant_leaves"]
test_set_type = "constant_treewidth"

make_range_of_files(range_max, constant, test_set_type, addRoots, folderName, truth_variable)
# make_files_constant_reticulations(numberOfLeavesMax, reticulation_constant, addRoots, folderName)
