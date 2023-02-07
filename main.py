import matplotlib.pyplot as plt

import BruteForce
import TreeContainment
import TreeDecomposition
import EmbeddingGenerator
import networkx as nx
import time
import ast
import TreewidthHeuristics
import BOTCH

# Example 1 (Super simple example):
# treeEdgeList = [("a", "b"), ("a", "c")]
# networkEdgeList = [("d", "b"), ("d", "c")]

# Example 2 (Main example):
# networkEdgeList = [("a", "b"), ("a", "c"), ("b", "e"), ("b", "d"), ("c", "d"), ("d", "f"), ("c", "g")]
# treeEdgeList = [("i", "h"), ("h", "e"), ("h", "f"), ("i", "g")]

# Example 3 (Return False)
# networkEdgeList = [("a", "b"), ("a", "c"), ("b", "e"), ("b", "d")]
# treeEdgeList = [("g", "f"), ("f", "c"), ("f", "d"), ("g", "e")]

# Example 4 (Non-compact path)
# networkEdgeList = [("a", "b"), ("a", "c"), ("b", "d"), ("b", "e"), ("c", "d"), ("c", "e"), ("d", "f"), ("e", "g")]
# treeEdgeList = [("h", "f"), ("h", "g")]

# Example 5 (Join node example)
# networkEdgeList = [("a", "b"), ("a", "c"), ("b", "d"), ("b", "e"), ("c", "f"), ("c", "g"),
#                    ("d", "h"), ("d", "i"), ("e", "h"), ("e", "i"), ("f", "j"), ("f", "k"),
#                    ("g", "j"), ("g", "k"), ("h", "l"), ("i", "m"), ("j", "n"), ("k", "o")]
# treeEdgeList = [("r", "p"), ("r", "q"), ("p", "l"), ("p", "m"), ("q", "n"), ("q", "o")]

# Example 6 (Join node example rooted)
# networkEdgeList = [("a", "b"), ("a", "c"), ("b", "d"), ("b", "e"), ("c", "f"), ("c", "g"),
#                    ("d", "h"), ("d", "i"), ("e", "h"), ("e", "i"), ("f", "j"), ("f", "k"),
#                    ("g", "j"), ("g", "k"), ("h", "l"), ("i", "m"), ("j", "n"), ("k", "o"), ("x", "a")]
# treeEdgeList = [("r", "p"), ("r", "q"), ("p", "l"), ("p", "m"), ("q", "n"), ("q", "o"), ("y", "r")]
#
# treeIn = nx.DiGraph(treeEdgeList)
# networkIn = nx.DiGraph(networkEdgeList)
# displayGraph = TreeDecomposition.display_graph_generator(treeIn, networkIn)  # Should we include leaves as output?
# outputTree = TreeDecomposition.nice_tree_decomposition(displayGraph)


if __name__ == '__main__':
    total_start = time.time()  # TODO: move this

    check = "algorithm_many_times"

    # if check == "main_algorithm_once":
    #     TreeContainment.main_algorithm(treeIn, networkIn)

    if check == "algorithm_many_times":
        iterate_min = 2
        iterate_max = 2
        # iterate_min = 5
        # iterate_max = 5
        # iterate_min = 0
        # iterate_max = 50
        safety_on = False
        scientific_on = True
        # skip_list = [6, 20, 31, 49, 57, 68, 83, 84, 89, 95]
        skip_list = []
        # Choose algorithm from ["path", "tree", "brute_force", "tc_brute_force"]
        algorithm = "tree"
        # Choose set from ["TestSet5Reticulations_True", "TestSet5Reticulations_False", "TestSet5Leaves_True", "TestSet5Leaves_False", "TestSet10Reticulations_True", "TestSet20Reticulations_True"]
        test_set_name = "TestSet5Ratio_True"
        # test_set_name = "TestSet2"

        for file_number in range(iterate_min, iterate_max + 1):
            if file_number in skip_list:
                continue
            file_string = "0000" + str(file_number)
            file_string = file_string[-4:]

            file = open(test_set_name + "\\" + "input" + file_string + ".txt", "r")
            line1 = file.read()
            line1 = line1.split("\n")
            file.close()
            print(20 * "=")
            print(f"TESTING input {file_string}")
            print(20 * "=")
            treeIn = nx.DiGraph()
            networkIn = nx.DiGraph()
            networkIn.add_edges_from(ast.literal_eval(line1[0]))
            treeIn.add_edges_from(ast.literal_eval(line1[1]))

            decomposition = None

            if algorithm == "path":
                # Get path decomposition
                # path_set_name = "TestSetPath" + test_set_name[-1]
                path_set_name = test_set_name + "_Paths"
                # print(path_set_name)
                file = open(path_set_name + "\\" + "path_input" + file_string + ".txt", "r")
                line = file.read()
                file.close()

                edge_list = ast.literal_eval(line)
                # print(edge_list)
                numbered_fix = TreeDecomposition.decomposition_numbering(edge_list)
                decomposition = TreeDecomposition.improved_nice_decomposition(numbered_fix, treeIn, networkIn)

            elif algorithm == "tree":
                # Get tree decomposition

                # TODO: remove this!
                # network_edge_list = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("b", "e"), ("d", "f"), ("c", "g")]
                # tree_edge_list = [("i", "h"), ("h", "e"), ("h", "f"), ("i", "g")]
                #
                # treeIn = nx.DiGraph(tree_edge_list)
                # networkIn = nx.DiGraph(network_edge_list)
                # TODO: remove this!

                display_graph = TreeDecomposition.display_graph_generator(treeIn, networkIn)
                td = TreeDecomposition.tree_decomposition(display_graph)
                decomposition = TreeDecomposition.improved_nice_decomposition(td, treeIn, networkIn)

            # Get the path/tree width
            if algorithm in ["tree", "path"]:
                decomposition_width = 0
                longest_bag = None
                for node in decomposition.nodes():
                    if len(node[1]) > decomposition_width:
                        decomposition_width = len(node[1])
                        longest_bag = node
                decomposition_width -= 1
                print(f"decomposition_width = {decomposition_width}")

            else:
                # Bruteforce:
                decomposition_width = 0

            if safety_on:
                try:
                    # Count leaves and reticulations
                    leaf_count = 0
                    reticulation_count = 0
                    for node in networkIn:
                        if networkIn.in_degree(node) == 2:
                            reticulation_count += 1
                        elif networkIn.out_degree(node) == 0:
                            leaf_count += 1

                    if algorithm in ["tree", "path"]:
                        start = time.time()
                        answer = TreeContainment.main_algorithm(treeIn, networkIn, decomposition)
                        end = time.time()
                    elif algorithm == "brute_force":
                        # Brute force
                        start = time.time()
                        answer, temp = BruteForce.brute_force(treeIn, networkIn)
                        end = time.time()
                    elif algorithm == "tc_brute_force":
                        # TC Brute force
                        start = time.time()
                        answer = BOTCH.tc_brute_force(treeIn, networkIn)
                        end = time.time()

                    print(answer)

                    # write answer to specific file
                    f = open("./" + test_set_name + "/hits_and_misses_" + algorithm +".txt", "a+")

                    if scientific_on:
                        f.write(file_string + ";" + str(leaf_count) + ";" + str(reticulation_count) + ";" + str(answer) + ";" + str(end - start) + ";" + str(decomposition_width) + "\n")

                    else:
                        if answer:
                            length_equalizer = " "
                        else:
                            length_equalizer = ""

                        f.write(file_string + "  ; " + str(answer) + length_equalizer + "    ; " + str(end - start)[:6] + "s ; " + str(decomposition_width) + "\n")
                    f.close()

                except:
                    end = time.time()
                    f = open("./" + test_set_name + "/hits_and_misses.txt", "a+")
                    f.write(file_string + "  ; " + "Crashed" + "  ; " + str(end - start)[:6] + "s ; " + str(decomposition_width) + "\n")
                    f.close()
            else:
                TreeDecomposition.display_graph_image(treeIn, networkIn)

                if algorithm in ["tree", "path"]:
                    TreeDecomposition.decomposition_printer(decomposition)
                    start = time.time()
                    answer = TreeContainment.main_algorithm(treeIn, networkIn, decomposition)
                    end = time.time()
                elif algorithm == "brute_force":
                    # Brute force
                    answer = BruteForce.brute_force(treeIn, networkIn)
                elif algorithm == "tc_brute_force":
                    # TC Brute force
                    answer = BOTCH.tc_brute_force(treeIn, networkIn)

    elif check == "tree_decomposition_test":
        iterate_min = 4
        iterate_max = 9
        average_tree_width = 0
        for file_number in range(iterate_min, iterate_max + 1):
            file_string = "0000" + str(file_number)
            file_string = file_string[-4:]

            file = open("TestSet2\\" + "input" + file_string + ".txt", "r")
            line1 = file.read()
            line1 = line1.split("\n")
            print(20 * "=")
            print(f"TESTING input {file_string}")
            print(20 * "=")
            treeIn = nx.DiGraph()
            networkIn = nx.DiGraph()
            networkIn.add_edges_from(ast.literal_eval(line1[0]))
            treeIn.add_edges_from(ast.literal_eval(line1[1]))
            display_graph = TreeDecomposition.display_graph_generator(treeIn, networkIn)
            tree_decomposition = TreeDecomposition.nice_tree_decomposition(display_graph)
            # TreeDecomposition.decomposition_printer(tree_decomposition)
            # print(tree_decomposition.nodes())

            tree_width = 0
            longest_bag = None
            for node in tree_decomposition.nodes():
                if len(node[1]) > tree_width:
                    tree_width = len(node[1])
                    longest_bag = node
            print(f"tree_width = {tree_width - 1}")
            # print(f"longest_bag = {longest_bag}")
            average_tree_width += tree_width

        average_tree_width = average_tree_width / (1.0 * iterate_max - iterate_min + 1) - 1
        print(f"\nAverage tree-width: {average_tree_width}")

    total_end = time.time()  # TODO: move this
    print(f"\nTotal Time elapsed: {total_end - total_start} seconds")

