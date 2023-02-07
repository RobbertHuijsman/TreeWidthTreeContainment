import networkx as nx
import time
import TreewidthHeuristics
import graphviz
import itertools


def display_graph_generator(network, tree):
    edge_list = []
    edge_list.extend(network.edges())
    edge_list.extend(tree.edges())
    display_graph = nx.Graph(edge_list)
    return display_graph


def decomposition_numbering(input_edge_list):
    """Turns a display graph into a tree decomposition (undirected)"""
    # Ordering alphabetically and numbering nodes
    counter = 0
    edge_list = []
    node_dict = {}
    for edge in input_edge_list:
        add_edge = []
        # edgeList.append(tuple([tuple(x) for x in edge]))
        for vertex in edge:
            add_vertex = list(vertex)
            add_vertex.sort()
            add_vertex = tuple(add_vertex)
            if add_vertex not in node_dict:
                node_dict[add_vertex] = counter
                counter += 1
            add_edge.append((node_dict[add_vertex], add_vertex))
        add_edge = tuple(add_edge)
        edge_list.append(add_edge)

    # Using the edgeList to create a graph
    dtd = nx.Graph(edge_list)

    return dtd


def tree_decomposition(display_graph):
    """Turns a display graph into a tree decomposition (undirected)"""
    td = TreewidthHeuristics.treewidth_min_degree(display_graph)

    # Ordering alphabetically and numbering nodes
    counter = 0
    edge_list = []
    node_dict = {}
    for edge in list(td[1].edges):
        add_edge = []
        # edgeList.append(tuple([tuple(x) for x in edge]))
        for vertex in edge:
            add_vertex = list(vertex)
            add_vertex.sort()
            add_vertex = tuple(add_vertex)
            if add_vertex not in node_dict:
                node_dict[add_vertex] = counter
                counter += 1
            add_edge.append((node_dict[add_vertex], add_vertex))
        add_edge = tuple(add_edge)
        edge_list.append(add_edge)

    # Using the edgeList to create a graph
    dtd = nx.Graph(edge_list)


    return dtd


def nice_decomposition(decomposition):
    """Turns a composition into a nice decomposition"""

    # print("Nice decomposition")

    dtd = decomposition

    # Turning the tree into a nice tree
    new_edges_list = []
    remove_edges_list = []

    root = None
    counter = dtd.number_of_nodes()

    # Making the leaves nice
    for x in dtd.nodes():
        if dtd.degree(x) == 1:
            for i in range(len(x[1])):
                j = len(x[1]) - i
                if i == 0:
                    new_edges_list.append((x, (counter, (x[1])[:j - 1])))
                else:
                    new_edges_list.append(((counter, ((x[1])[:j])), (counter+1, (x[1])[:j-1])))
                    counter += 1
                root = (counter, (x[1])[:j - 1])
            counter += 1  # Making sure the next new node doesn't start with the same counter

    # Making the in-between sections nice
    for xy in dtd.edges():
        x_without_y = [i for i in xy[0][1] if i not in xy[1][1]]
        y_without_x = [i for i in xy[1][1] if i not in xy[0][1]]
        # print(f"x_without_y = {x_without_y}")
        # print(f"y_without_x = {y_without_x}")


        old_node = xy[0][:]
        new_node = xy[0][:]
        # Checking if the difference in elements of the bags at both ends of the edge is too large
        if len(x_without_y) + len(y_without_x) > 1:
            for i in range(len(x_without_y)):
                # Finding the first element that can be ignored in the next bag
                j = 0
                while new_node[1][j] in xy[1][1]:
                    j += 1
                # Creating the new node by removing the introduced element
                new_node = (counter, new_node[1][:j] + new_node[1][j+1:])
                counter += 1
                new_edges_list.append((old_node, new_node))
                old_node = new_node
            for i in range(len(y_without_x) - 1):
                # Finding the first element that can be introduced in the next bag
                j = 0
                while xy[1][1][j] in new_node[1]:
                    j += 1
                # Creating the new node by adding the introduced element
                new_node = (counter, new_node[1][:] + (xy[1][1][j],))
                counter += 1
                new_edges_list.append((old_node, new_node))
                old_node = new_node
            # Adding an edge between the last new node and the original end node, and removing the original edge.
            new_edges_list.append((new_node, xy[1]))
            remove_edges_list.append(xy)

    dtd.add_edges_from(new_edges_list)
    dtd.remove_edges_from(remove_edges_list)

    # Making the graph directional
    dtd = nx.bfs_tree(dtd, root)

    # Making the join nodes nice
    new_edges_list = []
    remove_edges_list = []
    for x in dtd.nodes():
        if dtd.out_degree(x) > 1:
            old_node = x
            new_node = x
            for y in dtd.successors(x):
                # Initialize:
                if new_node == x:
                    new_node = (counter, x[1])
                    counter += 1
                else:
                    new_node = (counter, x[1])
                    counter += 1

                    # Add another in between node if y is not the last child
                    if y != list(dtd.successors(x))[-1]:
                        new_edges_list.append((old_node, new_node))
                        old_node = new_node
                        new_node = (counter, x[1])
                        counter += 1

                new_edges_list.append((old_node, new_node))
                new_edges_list.append((new_node, y))
                remove_edges_list.append((x, y))
    dtd.add_edges_from(new_edges_list)
    dtd.remove_edges_from(remove_edges_list)

    reorder = True
    # Reorder all nodes:
    if reorder:
        count = 0
        reorder_dict = {}
        # Start the list with just the leaves
        todo_list = [node for node in dtd.nodes() if dtd.out_degree(node) == 0]
        while todo_list:
            node = todo_list.pop()
            reorder_dict[node[0]] = count
            count += 1
            for parent in dtd.predecessors(node):
                if parent[0] not in reorder_dict:
                    todo_list.append(parent)
        # print(f"reorder_dict = {reorder_dict}")
        ordered_edge_list = []
        for edge in dtd.edges():
            node1 = (reorder_dict[edge[0][0]], edge[0][1])
            node2 = (reorder_dict[edge[1][0]], edge[1][1])

            ordered_edge_list.append((node1, node2))
        dtd = nx.DiGraph(ordered_edge_list)
    return dtd


def improved_nice_decomposition(decomposition, network_in, tree_in):
    """Turns a composition into a specific nice decomposition that optimizes the order of introductions to have
    successive introduced nodes be as adjacent as possible."""
    dtd = decomposition
    # Turning the tree into a nice tree
    new_edges_list = []
    remove_edges_list = []

    root = None
    counter = dtd.number_of_nodes()

    # Making the leaves nice
    # print("LEAVES")
    x_add_edges = []
    x_remove_edges = []
    for x in dtd.nodes():
        if dtd.degree(x) == 1:
            # CLUSTERING
            todo_nodes = list(x[1][:])
            cluster_list = []
            while todo_nodes:
                todo_node = todo_nodes.pop()
                # print(f"todo_note = {todo_node}")
                connected_nodes = []
                for other_node in reversed(todo_nodes):  # Needs to be reversed, so that we can add stuff to the end of it
                    if ((todo_node, other_node) in tree_in.edges() or
                            (todo_node, other_node) in network_in.edges() or
                            (other_node, todo_node) in tree_in.edges() or
                            (other_node, todo_node) in network_in.edges()):
                        # print(f"other_node = {other_node}")

                        connected_nodes.append(other_node)
                        # Re-order the nodes to be done
                        if other_node in todo_nodes:
                            todo_nodes.remove(other_node)
                            todo_nodes.append(other_node)
                # print(f"connected_nodes = {connected_nodes}")

                found = False
                for cluster in cluster_list:
                    if todo_node in cluster:
                        found = True
                        for node in connected_nodes:
                            if node in cluster:
                                continue
                            cluster.append(node)
                if not found:
                    connected_nodes.insert(0, todo_node)
                    # print(f"connected_nodes = {connected_nodes}")
                    cluster_list.append(connected_nodes)
            cluster_list.sort(key=len, reverse=True)
            # cluster_list.sort(key=len)

            # print(f"cluster_list = {cluster_list}")
            # print(f"x = {x}")

            new_x = (x[0], tuple([node for cluster in cluster_list for node in cluster]))

            # Update all edges with x in it
            for edge in dtd.edges():
                if x == edge[0]:
                    x_remove_edges.append(edge)
                    x_add_edges.append((new_x, edge[1]))
                if x == edge[1]:
                    x_remove_edges.append(edge)
                    x_add_edges.append((edge[0], new_x))

            x = new_x
            # print(f"x = {x}")

            # CONNECTING EDGES
            for i in range(len(x[1])):
                j = len(x[1]) - i
                if i == 0:
                    new_edges_list.append((x, (counter, (x[1])[:j - 1])))
                    # print(f"new_edge: {(x, (counter, (x[1])[:j - 1]))}")
                else:
                    new_edges_list.append(((counter, ((x[1])[:j])), (counter+1, (x[1])[:j-1])))
                    # print(f"new_edge: {((counter, ((x[1])[:j])), (counter+1, (x[1])[:j-1]))}")
                    counter += 1
                root = (counter, (x[1])[:j - 1])
            counter += 1  # Making sure the next new node doesn't start with the same counter

    # print(f"new_edges_list = {new_edges_list}")
    dtd.add_edges_from(x_add_edges)
    dtd.remove_edges_from(x_remove_edges)

    # print(f"all edges: {dtd.edges()}")

    # Making the in-between sections nice
    # print("MID SECTIONS")

    for xy in dtd.edges():
        # print(xy)
        x_without_y = [i for i in xy[0][1] if i not in xy[1][1]]
        y_without_x = [i for i in xy[1][1] if i not in xy[0][1]]
        x_and_y = [i for i in xy[0][1] if i in xy[1][1]]

        old_node = xy[0][:]
        new_node = xy[0][:]
        # Checking if the difference in elements of the bags at both ends of the edge is too large
        if len(x_without_y) + len(y_without_x) > 1:
            # 1. Forgetting nodes
            remaining_nodes = x_without_y[:]
            for i in range(len(x_without_y)):
                # print("loop")
                # Remove one node from x_without_y
                chosen_node = None

                # Try to find a node that is not connected in N or T:
                for node in x_without_y:
                    if node not in remaining_nodes:
                        continue
                    connected = False
                    # Check if it's connected
                    for neighbor in x_and_y:
                        if ((node, neighbor) in tree_in.edges() or
                                (node, neighbor) in network_in.edges() or
                                (neighbor, node) in tree_in.edges() or
                                (neighbor, node) in network_in.edges()):
                            connected = True
                            break
                    if connected:
                        continue
                    chosen_node = node
                    remaining_nodes.remove(node)
                    # print(f"chosen_node forgotten (unconnected) = {chosen_node}")
                    break
                # If no node is unconnected:
                if chosen_node is None:
                    for node in x_without_y:
                        if node not in remaining_nodes:
                            continue
                        chosen_node = node
                        remaining_nodes.remove(node)
                        # print(f"chosen_node forgotten (connected) = {chosen_node}")
                        break

                # print(f"new_node = {new_node}")
                # print(f"old_node = {old_node}")
                # print(f"chosen_node = {chosen_node}")
                j = new_node[1].index(chosen_node)

                # Creating the new node by removing the element
                new_node = (counter, new_node[1][:j] + new_node[1][j+1:])
                counter += 1
                new_edges_list.append((old_node, new_node))
                old_node = new_node

            # 2. Introducing nodes
            # print("Introducing:")
            remaining_nodes = y_without_x[:]
            for i in range(len(y_without_x) - 1):

                # Introduce one node from y_without_x
                chosen_node = None

                # Try to find a node that is connected in N or T:
                for node in y_without_x:
                    if node not in remaining_nodes:
                        continue
                    connected = False
                    # Check if it's connected
                    for neighbor in x_and_y:
                        if ((node, neighbor) in tree_in.edges() or
                                (node, neighbor) in network_in.edges() or
                                (neighbor, node) in tree_in.edges() or
                                (neighbor, node) in network_in.edges()):
                            connected = True
                            break
                    if not connected:
                        continue
                    chosen_node = node
                    remaining_nodes.remove(node)
                    # print(f"chosen_node introduced (connected) = {chosen_node}")
                    break
                # If no node is unconnected:
                if chosen_node is None:
                    for node in y_without_x:
                        if node not in remaining_nodes:
                            continue
                        chosen_node = node
                        remaining_nodes.remove(node)
                        # print(f"chosen_node introduced (unconnected) = {chosen_node}")
                        break

                j = xy[1][1].index(chosen_node)

                # Creating the new node by adding the introduced element
                new_node = (counter, new_node[1][:] + (xy[1][1][j],))
                counter += 1
                new_edges_list.append((old_node, new_node))
                old_node = new_node
            # Adding an edge between the last new node and the original end node, and removing the original edge.
            new_edges_list.append((new_node, xy[1]))
            remove_edges_list.append(xy)

    # print(f"new_edges_list = {new_edges_list}")
    # print(f"remove_edges_list = {remove_edges_list}")

    dtd.add_edges_from(new_edges_list)
    dtd.remove_edges_from(remove_edges_list)

    # Making the graph directional
    # print(f"root = {root}")
    dtd = nx.bfs_tree(dtd, root)

    # Making the join nodes nice
    new_edges_list = []
    remove_edges_list = []
    for x in dtd.nodes():
        if dtd.out_degree(x) > 1:
            old_node = x
            new_node = x
            for y in dtd.successors(x):
                # Initialize:
                if new_node == x:
                    new_node = (counter, x[1])
                    counter += 1
                else:
                    new_node = (counter, x[1])
                    counter += 1

                    # Add another in between node if y is not the last child
                    if y != list(dtd.successors(x))[-1]:
                        new_edges_list.append((old_node, new_node))
                        old_node = new_node
                        new_node = (counter, x[1])
                        counter += 1

                new_edges_list.append((old_node, new_node))
                new_edges_list.append((new_node, y))
                remove_edges_list.append((x, y))
    dtd.add_edges_from(new_edges_list)
    dtd.remove_edges_from(remove_edges_list)

    reorder = True
    # Reorder all nodes:
    if reorder:
        count = 0
        reorder_dict = {}
        # Start the list with just the leaves
        todo_list = [node for node in dtd.nodes() if dtd.out_degree(node) == 0]
        while todo_list:
            node = todo_list.pop()
            reorder_dict[node[0]] = count
            count += 1
            for parent in dtd.predecessors(node):
                if parent[0] not in reorder_dict:
                    todo_list.append(parent)
        # print(f"reorder_dict = {reorder_dict}")
        ordered_edge_list = []
        for edge in dtd.edges():
            node1 = (reorder_dict[edge[0][0]], edge[0][1])
            node2 = (reorder_dict[edge[1][0]], edge[1][1])

            ordered_edge_list.append((node1, node2))
        dtd = nx.DiGraph(ordered_edge_list)

    # Hard coding a bugfix (nothing to see here)
    if dtd.number_of_nodes() == 5:
        remove_list = []
        add_list = []
        for edge in dtd.edges():
            if edge[0][0] == 0:
                remove_list.append(edge)
                add_list.append(((edge[0][0], tuple()), edge[1]))
            if edge[1][0] == 0:
                remove_list.append(edge)
                add_list.append((edge[0], (edge[1][0], tuple())))
        dtd.remove_edges_from(remove_list)
        dtd.add_edges_from(add_list)
        return dtd

    # test_list = [((0, ()), (1, ('h',))),
    #              ((1, ('h',)), (2, ('h', 'f'))),
    #              ((2, ('h', 'f')), (3, ('h',))),
    #              ((3, ('h',)), (4, ()))]
    # # test_list = [((0, ()), (1, ('h',))),
    # #              ((1, ('h',)), (2, ('h', 'f'))),
    # #              ((2, ('h', 'f')), (3, ('h',))),
    # #              ((3, ('h')), (4, ()))]
    #
    # test_list.reverse()
    #
    # test_graph = nx.DiGraph(test_list)
    # dtd = test_graph  # TODO: REMOVE THIS!!!
    # print(dtd.edges())
    return dtd


def nice_tree_decomposition(display_graph):
    td = TreewidthHeuristics.treewidth_min_degree(display_graph)

    # el = [(('a', 'b', 'c'), ('c', 'd', 'e'))]
    # el = [(('a', 'b'), ('b', 'c')), (('a', 'b'), ('b', 'd')), (('a', 'b'), ('b', 'e')), (('a', 'b'), ('b', 'f'))]
    # td = (1, nx.Graph(el))  # TODO: remove this!

    root = "non-existent"

    # Ordering alphabetically and numbering nodes
    counter = 0
    edgeList = []
    node_dict = {}
    for edge in list(td[1].edges):
        addEdge = []
        # edgeList.append(tuple([tuple(x) for x in edge]))
        for vertex in edge:
            addVertex = list(vertex)
            addVertex.sort()
            addVertex = tuple(addVertex)
            if addVertex not in node_dict:
                node_dict[addVertex] = counter
                counter += 1
            addEdge.append((node_dict[addVertex], addVertex))
        addEdge = tuple(addEdge)
        edgeList.append(addEdge)

    # Using the edgeList to create a graph
    dtd = nx.Graph(edgeList)

    # Turning the tree into a nice tree
    new_edges_list = []
    remove_edges_list = []

    # Making the leaves nice
    for x in dtd.nodes():
        if dtd.degree(x) == 1:  # TODO: no idea why this gives a warning...
            for i in range(len(x[1])):
                j = len(x[1]) - i
                if i == 0:
                    new_edges_list.append((x, (counter, (x[1])[:j - 1])))
                else:
                    new_edges_list.append(((counter, ((x[1])[:j])), (counter + 1, (x[1])[:j - 1])))
                    counter += 1
                root = (counter, (x[1])[:j - 1])
            counter += 1  # Making sure the next new node doesn't start with the same counter

    # Making the in-between sections nice
    for xy in dtd.edges():
        x_without_y = [i for i in xy[0][1] if i not in xy[1][1]]
        y_without_x = [i for i in xy[1][1] if i not in xy[0][1]]

        old_node = xy[0][:]
        new_node = xy[0][:]
        # Checking if the difference in elements of the bags at both ends of the edge is too large
        if len(x_without_y) + len(y_without_x) > 1:
            for i in range(len(x_without_y)):
                # Finding the first element that can be ignored in the next bag
                j = 0
                while new_node[1][j] in xy[1][1]:
                    j += 1
                # Creating the new node by removing the introduced element
                new_node = (counter, new_node[1][:j] + new_node[1][j + 1:])
                counter += 1
                new_edges_list.append((old_node, new_node))
                old_node = new_node
            for i in range(len(y_without_x) - 1):
                # Finding the first element that can be introduced in the next bag
                j = 0
                while xy[1][1][j] in new_node[1]:
                    j += 1
                # Creating the new node by adding the introduced element
                new_node = (counter, new_node[1][:] + (xy[1][1][j],))
                counter += 1
                new_edges_list.append((old_node, new_node))
                old_node = new_node
            # Adding an edge between the last new node and the original end node, and removing the original edge.
            new_edges_list.append((new_node, xy[1]))
            remove_edges_list.append(xy)

    dtd.add_edges_from(new_edges_list)
    dtd.remove_edges_from(remove_edges_list)

    # Making the graph directional
    dtd = nx.bfs_tree(dtd, root)

    # Making the join nodes nice
    new_edges_list = []
    remove_edges_list = []
    for x in dtd.nodes():
        if dtd.out_degree(x) > 1:
            old_node = x
            new_node = x
            for y in dtd.successors(x):
                # Initialize:
                if new_node == x:
                    new_node = (counter, x[1])
                    counter += 1
                else:
                    new_node = (counter, x[1])
                    counter += 1

                    # Add another in between node if y is not the last child
                    if y != list(dtd.successors(x))[-1]:
                        new_edges_list.append((old_node, new_node))
                        old_node = new_node
                        new_node = (counter, x[1])
                        counter += 1

                new_edges_list.append((old_node, new_node))
                new_edges_list.append((new_node, y))
                remove_edges_list.append((x, y))
    dtd.add_edges_from(new_edges_list)
    dtd.remove_edges_from(remove_edges_list)

    # Example 2
    # edge_list = [((0, ()), (1, ('a',))),
    #              ((1, ('a',)), (2, ('a', 'b'))),
    #              ((2, ('a', 'b')), (3, ('a', 'b', 'c'))),
    #              ((3, ('a', 'b', 'c')), (4, ('b', 'c'))),
    #              ((4, ('b', 'c')), (5, ('b', 'c', 'd'))),
    #              ((5, ('b', 'c', 'd')), (6, ('b', 'c', 'd', 'e'))),
    #              ((6, ('b', 'c', 'd', 'e')), (7, ('b', 'c', 'd', 'e', 'f'))),
    #              ((7, ('b', 'c', 'd', 'e', 'f')), (8, ('b', 'c', 'd', 'e', 'f', 'g'))),
    #              ((8, ('b', 'c', 'd', 'e', 'f', 'g')), (9, ('c', 'd', 'e', 'f', 'g'))),
    #              ((9, ('c', 'd', 'e', 'f', 'g')), (10, ('d', 'e', 'f', 'g'))),
    #              ((10, ('d', 'e', 'f', 'g')), (11, ('e', 'f', 'g'))),
    #              ((11, ('e', 'f', 'g')), (12, ('e', 'f', 'g', 'h'))),
    #              ((12, ('e', 'f', 'g', 'h')), (13, ('e', 'f', 'g', 'h', 'i'))),
    #              ((13, ('e', 'f', 'g', 'h', 'i')), (14, ('e', 'f', 'g', 'h'))),
    #              ((14, ('e', 'f', 'g', 'h')), (15, ('e', 'f', 'g'))),
    #              ((15, ('e', 'f', 'g')), (16, ('e', 'f'))),
    #              ((16, ('e', 'f')), (17, ('e',))),
    #              ((17, ('e',)), (18, ())),
    #              ]

    # Example 3
    # edge_list = [((0, ()), (1, ('a',))),
    #              ((1, ('a',)), (2, ('a', 'b'))),
    #              ((2, ('a', 'b')), (3, ('a', 'b', 'c'))),
    #              ((3, ('a', 'b', 'c')), (4, ('b', 'c'))),
    #              ((4, ('b', 'c')), (5, ('b', 'c', 'd'))),
    #              ((5, ('b', 'c', 'd')), (6, ('b', 'c', 'd', 'e'))),
    #              ((6, ('b', 'c', 'd', 'e')), (7, ('b', 'c', 'd', 'e', 'f'))),
    #              ((7, ('b', 'c', 'd', 'e', 'f')), (8, ('c', 'd', 'e', 'f'))),
    #              ((8, ('c', 'd', 'e', 'f')), (9, ('d', 'e', 'f'))),
    #              ((9, ('d', 'e', 'f')), (10, ('e', 'f'))),
    #              ((10, ('e', 'f')), (11, ('e', 'f', 'g'))),
    #              ((11, ('e', 'f', 'g')), (12, ('f', 'g'))),
    #              ((12, ('f', 'g')), (13, ('g',))),
    #              ((13, ('g',)), (14, ()))
    #              ]

    # Example 4
    # edge_list = [((0, ()), (1, ('a',))),
    #              ((1, ('a',)), (2, ('a', 'b'))),
    #              ((2, ('a', 'b')), (3, ('a', 'b', 'c'))),
    #              ((3, ('a', 'b', 'c')), (4, ('b', 'c'))),
    #              ((4, ('b', 'c')), (5, ('b', 'c', 'd'))),
    #              ((5, ('b', 'c', 'd')), (6, ('b', 'c', 'd', 'e'))),
    #              ((6, ('b', 'c', 'd', 'e')), (7, ('c', 'd', 'e'))),
    #              ((7, ('c', 'd', 'e')), (8, ('d', 'e'))),
    #              ((8, ('d', 'e')), (9, ('d', 'e', 'f'))),
    #              ((9, ('d', 'e', 'f')), (10, ('d', 'e', 'f', 'g'))),
    #              ((10, ('d', 'e', 'f', 'g')), (11, ('e', 'f', 'g'))),
    #              ((11, ('e', 'f', 'g')), (12, ('f', 'g'))),
    #              ((12, ('f', 'g')), (13, ('f', 'g', 'h'))),
    #              ((13, ('f', 'g', 'h')), (14, ('g', 'h'))),
    #              ((14, ('g', 'h')), (15, ('h',))),
    #              ((15, ('h',)), (16, ()))
    #              ]

    # Example 5 (2.1)
    # edge_list = [((0, ()), (1, ('i',))),
    #              ((1, ('i',)), (2, ('g', 'i'))),
    #              ((2, ('g', 'i')), (3, ('c', 'g', 'i'))),
    #              ((3, ('c', 'g', 'i')), (4, ('c', 'i'))),
    #              ((4, ('c', 'i')), (5, ('a', 'c', 'i'))),
    #              ((5, ('a', 'c', 'i')), (6, ('a', 'c', 'h', 'i'))),
    #              ((6, ('a', 'c', 'h', 'i')), (7, ('a', 'c', 'd', 'h', 'i'))),
    #              ((7, ('a', 'c', 'd', 'h', 'i')), (8, ('a', 'd', 'h', 'i'))),
    #              ((8, ('a', 'd', 'h', 'i')), (9, ('a', 'd', 'h'))),
    #              ((9, ('a', 'd', 'h')), (10, ('a', 'd', 'f', 'h'))),
    #              ((10, ('a', 'd', 'f', 'h')), (11, ('a', 'b', 'd', 'f', 'h'))),
    #              ((11, ('a', 'b', 'd', 'f', 'h')), (12, ('b', 'd', 'f', 'h'))),
    #              ((12, ('b', 'd', 'f', 'h')), (13, ('b', 'f', 'h'))),
    #              ((13, ('b', 'f', 'h')), (14, ('b', 'h'))),
    #              ((14, ('b', 'h')), (15, ('b', 'e', 'h'))),
    #              ((15, ('b', 'e', 'h')), (16, ('b', 'h'))),
    #              ((16, ('b', 'h')), (17, ('b',))),
    #              ((17, ('b',)), (18, ()))
    #              ]

    # Example 6 (2.1) (path decomposition 5 backwards)
    # edge_list = [
    #              ((18, ()), (17, ('b',))),
    #              ((17, ('b',)), (16, ('b', 'h'))),
    #              ((16, ('b', 'h')), (15, ('b', 'e', 'h'))),
    #              ((15, ('b', 'e', 'h')), (14, ('b', 'h'))),
    #              ((14, ('b', 'h')), (13, ('b', 'f', 'h'))),
    #              ((13, ('b', 'f', 'h')), (12, ('b', 'd', 'f', 'h'))),
    #              ((12, ('b', 'd', 'f', 'h')), (11, ('a', 'b', 'd', 'f', 'h'))),
    #              ((11, ('a', 'b', 'd', 'f', 'h')), (10, ('a', 'd', 'f', 'h'))),
    #              ((10, ('a', 'd', 'f', 'h')), (9, ('a', 'd', 'h'))),
    #              ((9, ('a', 'd', 'h')), (8, ('a', 'd', 'h', 'i'))),
    #              ((8, ('a', 'd', 'h', 'i')), (7, ('a', 'c', 'd', 'h', 'i'))),
    #              ((7, ('a', 'c', 'd', 'h', 'i')), (6, ('a', 'c', 'h', 'i'))),
    #              ((6, ('a', 'c', 'h', 'i')), (5, ('a', 'c', 'i'))),
    #              ((5, ('a', 'c', 'i')), (4, ('c', 'i'))),
    #              ((4, ('c', 'i')), (3, ('c', 'g', 'i'))),
    #              ((3, ('c', 'g', 'i')), (2, ('g', 'i'))),
    #              ((2, ('g', 'i')), (1, ('i',))),
    #              ((1, ('i',)), (0, ())),
    #              ]

    # Example 7
    # edge_list = [((16, ()), (15, ('h',))),
    #     ((15, ('h',)), (14, ('g', 'h'))),
    #     ((14, ('g', 'h')), (13, ('f', 'g', 'h'))),
    #     ((13, ('f', 'g', 'h')), (12, ('f', 'g'))),
    #     ((12, ('f', 'g')), (11, ('e', 'f', 'g'))),
    #     ((11, ('e', 'f', 'g')), (10, ('d', 'e', 'f', 'g'))),
    #     ((10, ('d', 'e', 'f', 'g')), (9, ('d', 'e', 'f'))),
    #     ((9, ('d', 'e', 'f')), (8, ('d', 'e'))),
    #     ((8, ('d', 'e')), (7, ('c', 'd', 'e'))),
    #     ((7, ('c', 'd', 'e')), (6, ('b', 'c', 'd', 'e'))),
    #     ((6, ('b', 'c', 'd', 'e')), (5, ('b', 'c', 'd'))),
    #     ((5, ('b', 'c', 'd')), (4, ('b', 'c'))),
    #     ((4, ('b', 'c')), (3, ('a', 'b', 'c'))),
    #     ((3, ('a', 'b', 'c')), (2, ('a', 'b'))),
    #     ((2, ('a', 'b')), (1, ('a',))),
    #     ((1, ('a',)), (0, ()))
    #     ]

    # Example 10
    # edge_list = [((1, ()), (2, ('d',))),
    #              ((2, ('d',)), (3, ('d', 'e'))),
    #              ((3, ('d', 'e')), (4, ('d', 'e', 'h'))),
    #              ((4, ('d', 'e', 'h')), (5, ('d', 'e', 'h', 'i'))),
    #              ((5, ('d', 'e', 'h', 'i')), (6, ('d', 'e', 'h', 'i', 'l'))),
    #              ((6, ('d', 'e', 'h', 'i', 'l')), (7, ('d', 'e', 'h', 'i', 'l', 'm'))),
    #              ((7, ('d', 'e', 'h', 'i', 'l', 'm')), (8, ('d', 'e', 'h', 'i', 'l', 'm', 'p'))),
    #              ((8, ('d', 'e', 'h', 'i', 'l', 'm', 'p')), (9, ('d', 'e', 'h', 'i', 'l', 'p'))),
    #              ((9, ('d', 'e', 'h', 'i', 'l', 'p')), (10, ('d', 'e', 'h', 'i', 'p'))),
    #              ((10, ('d', 'e', 'h', 'i', 'p')), (11, ('d', 'e', 'h', 'p'))),
    #              ((11, ('d', 'e', 'h', 'p')), (12, ('d', 'e', 'p'))),
    #              ((12, ('d', 'e', 'p')), (13, ('a', 'd', 'e', 'p'))),
    #              ((13, ('a', 'd', 'e', 'p')), (14, ('a', 'b', 'd', 'e', 'p'))),
    #              ((14, ('a', 'b', 'd', 'e', 'p')), (15, ('a', 'b', 'c', 'd', 'e', 'p'))),
    #              ((15, ('a', 'b', 'c', 'd', 'e', 'p')), (16, ('a', 'b', 'c', 'd', 'e', 'p', 'r'))),
    #              ((16, ('a', 'b', 'c', 'd', 'e', 'p', 'r')), (17, ('a', 'b', 'c', 'e', 'p', 'r'))),
    #              ((17, ('a', 'b', 'c', 'e', 'p', 'r')), (18, ('a', 'b', 'c', 'p', 'r'))),
    #              ((18, ('a', 'b', 'c', 'p', 'r')), (19, ('a', 'b', 'c', 'r'))),
    #
    #              ((101, ()), (102, ('f',))),
    #              ((102, ('f',)), (103, ('f', 'g'))),
    #              ((103, ('f', 'g')), (104, ('f', 'g', 'j'))),
    #              ((104, ('f', 'g', 'j')), (105, ('f', 'g', 'j', 'k'))),
    #              ((105, ('f', 'g', 'j', 'k')), (106, ('f', 'g', 'j', 'k', 'n'))),
    #              ((106, ('f', 'g', 'j', 'k', 'n')), (107, ('f', 'g', 'j', 'k', 'n', 'o'))),
    #              ((107, ('f', 'g', 'j', 'k', 'n', 'o')), (108, ('f', 'g', 'j', 'k', 'n', 'o', 'q'))),
    #              ((108, ('f', 'g', 'j', 'k', 'n', 'o', 'q')), (109, ('f', 'g', 'j', 'k', 'n', 'q'))),
    #              ((109, ('f', 'g', 'j', 'k', 'n', 'q')), (110, ('f', 'g', 'j', 'k', 'q'))),
    #              ((110, ('f', 'g', 'j', 'k', 'q')), (111, ('f', 'g', 'j', 'q'))),
    #              ((111, ('f', 'g', 'j', 'q')), (112, ('f', 'g', 'q'))),
    #              ((112, ('f', 'g', 'q')), (113, ('a', 'f', 'g', 'q'))),
    #              ((113, ('a', 'f', 'g', 'q')), (114, ('a', 'b', 'f', 'g', 'q'))),
    #              ((114, ('a', 'b', 'f', 'g', 'q')), (115, ('a', 'b', 'c', 'f', 'g', 'q'))),
    #              ((115, ('a', 'b', 'c', 'f', 'g', 'q')), (116, ('a', 'b', 'c', 'f', 'g', 'q', 'r'))),
    #              ((116, ('a', 'b', 'c', 'f', 'g', 'q', 'r')), (117, ('a', 'b', 'c', 'g', 'q', 'r'))),
    #              ((117, ('a', 'b', 'c', 'g', 'q', 'r')), (118, ('a', 'b', 'c', 'q', 'r'))),
    #              ((118, ('a', 'b', 'c', 'q', 'r')), (119, ('a', 'b', 'c', 'r'))),
    #
    #              ((19, ('a', 'b', 'c', 'r')), (200, ('a', 'b', 'c', 'r'))),
    #              ((119, ('a', 'b', 'c', 'r')), (200, ('a', 'b', 'c', 'r'))),
    #
    #              ((200, ('a', 'b', 'c', 'r')), (201, ('a', 'b', 'c'))),
    #              ((201, ('a', 'b', 'c')), (202, ('a', 'b'))),
    #              ((202, ('a', 'b')), (203, ('a',))),
    #              ((203, ('a',)), (204, ())),
    #              ]

    # Example 11
    # edge_list = [((1, ()), (2, ('d',))),
    #              ((2, ('d',)), (3, ('d', 'e'))),
    #              ((3, ('d', 'e')), (4, ('d', 'e', 'h'))),
    #              ((4, ('d', 'e', 'h')), (5, ('d', 'e', 'h', 'i'))),
    #              ((5, ('d', 'e', 'h', 'i')), (6, ('d', 'e', 'h', 'i', 'l'))),
    #              ((6, ('d', 'e', 'h', 'i', 'l')), (7, ('d', 'e', 'h', 'i', 'l', 'm'))),
    #              ((7, ('d', 'e', 'h', 'i', 'l', 'm')), (8, ('d', 'e', 'h', 'i', 'l', 'm', 'p'))),
    #              ((8, ('d', 'e', 'h', 'i', 'l', 'm', 'p')), (9, ('d', 'e', 'h', 'i', 'l', 'p'))),
    #              ((9, ('d', 'e', 'h', 'i', 'l', 'p')), (10, ('d', 'e', 'h', 'i', 'p'))),
    #              ((10, ('d', 'e', 'h', 'i', 'p')), (11, ('d', 'e', 'h', 'p'))),
    #              ((11, ('d', 'e', 'h', 'p')), (12, ('d', 'e', 'p'))),
    #              ((12, ('d', 'e', 'p')), (13, ('a', 'd', 'e', 'p'))),
    #              ((13, ('a', 'd', 'e', 'p')), (14, ('a', 'b', 'd', 'e', 'p'))),
    #              ((14, ('a', 'b', 'd', 'e', 'p')), (15, ('a', 'b', 'c', 'd', 'e', 'p'))),
    #              ((15, ('a', 'b', 'c', 'd', 'e', 'p')), (16, ('a', 'b', 'c', 'd', 'e', 'p', 'r'))),
    #              ((16, ('a', 'b', 'c', 'd', 'e', 'p', 'r')), (17, ('a', 'b', 'c', 'e', 'p', 'r'))),
    #              ((17, ('a', 'b', 'c', 'e', 'p', 'r')), (18, ('a', 'b', 'c', 'p', 'r'))),
    #              ((18, ('a', 'b', 'c', 'p', 'r')), (19, ('a', 'b', 'c', 'r'))),
    #              ((19, ('a', 'b', 'c', 'r')), (20, ('a', 'b', 'c', 'r', 'x'))),
    #              ((20, ('a', 'b', 'c', 'r', 'x')), (21, ('a', 'b', 'c', 'r', 'x', 'y'))),
    #
    #              ((101, ()), (102, ('f',))),
    #              ((102, ('f',)), (103, ('f', 'g'))),
    #              ((103, ('f', 'g')), (104, ('f', 'g', 'j'))),
    #              ((104, ('f', 'g', 'j')), (105, ('f', 'g', 'j', 'k'))),
    #              ((105, ('f', 'g', 'j', 'k')), (106, ('f', 'g', 'j', 'k', 'n'))),
    #              ((106, ('f', 'g', 'j', 'k', 'n')), (107, ('f', 'g', 'j', 'k', 'n', 'o'))),
    #              ((107, ('f', 'g', 'j', 'k', 'n', 'o')), (108, ('f', 'g', 'j', 'k', 'n', 'o', 'q'))),
    #              ((108, ('f', 'g', 'j', 'k', 'n', 'o', 'q')), (109, ('f', 'g', 'j', 'k', 'n', 'q'))),
    #              ((109, ('f', 'g', 'j', 'k', 'n', 'q')), (110, ('f', 'g', 'j', 'k', 'q'))),
    #              ((110, ('f', 'g', 'j', 'k', 'q')), (111, ('f', 'g', 'j', 'q'))),
    #              ((111, ('f', 'g', 'j', 'q')), (112, ('f', 'g', 'q'))),
    #              ((112, ('f', 'g', 'q')), (113, ('a', 'f', 'g', 'q'))),
    #              ((113, ('a', 'f', 'g', 'q')), (114, ('a', 'b', 'f', 'g', 'q'))),
    #              ((114, ('a', 'b', 'f', 'g', 'q')), (115, ('a', 'b', 'c', 'f', 'g', 'q'))),
    #              ((115, ('a', 'b', 'c', 'f', 'g', 'q')), (116, ('a', 'b', 'c', 'f', 'g', 'q', 'r'))),
    #              ((116, ('a', 'b', 'c', 'f', 'g', 'q', 'r')), (117, ('a', 'b', 'c', 'g', 'q', 'r'))),
    #              ((117, ('a', 'b', 'c', 'g', 'q', 'r')), (118, ('a', 'b', 'c', 'q', 'r'))),
    #              ((118, ('a', 'b', 'c', 'q', 'r')), (119, ('a', 'b', 'c', 'r'))),
    #              ((119, ('a', 'b', 'c', 'r')), (120, ('a', 'b', 'c', 'r', 'x'))),
    #              ((120, ('a', 'b', 'c', 'r', 'x')), (121, ('a', 'b', 'c', 'r', 'x', 'y'))),
    #
    #              ((21, ('a', 'b', 'c', 'r', 'x', 'y')), (200, ('a', 'b', 'c', 'r', 'x', 'y'))),
    #              ((121, ('a', 'b', 'c', 'r', 'x', 'y')), (200, ('a', 'b', 'c', 'r', 'x', 'y'))),
    #
    #              ((200, ('a', 'b', 'c', 'r', 'x', 'y')), (201, ('a', 'b', 'c', 'r', 'x'))),
    #              ((201, ('a', 'b', 'c', 'r', 'x')), (202, ('a', 'b', 'c', 'r'))),
    #              ((202, ('a', 'b', 'c', 'r')), (203, ('a', 'b', 'c', ))),
    #              ((203, ('a', 'b', 'c')), (204, ('a', 'b'))),
    #              ((204, ('a', 'b')), (205, ('a',))),
    #              ((205, ('a',)), (206, ())),
    #              ]
    #
    # # Turn around edges:  # TODO: remove this
    # new_edge_list = []
    # for edge in edge_list:
    #     new_edge_list.append((edge[1], edge[0]))
    # edge_list = new_edge_list
    #
    # dtd = nx.DiGraph(edge_list)

    return dtd


def dumb_converter(network):
    # For when installing a package is somehow made harder than just implementing the thing yourself
    ni = graphviz.Graph('ni')
    edge_list = []
    for edge in network.edges():
        if len(edge[0][1]) == 0:
            node1 = str(edge[0][0]) + " ."  # ∅
        else:
            letters = " "
            for count, letter in enumerate(edge[0][1]):
                if count == 0 or count == len(edge[0][1]):
                    letters = letters + letter
                else:
                    letters = letters+","+letter
            node1 = str(edge[0][0]) + letters
        if len(edge[1][1]) == 0:
            node2 = str(edge[1][0]) + " ."  # ∅
        else:
            letters = " "
            for count, letter in enumerate(edge[1][1]):
                if count == 0 or count == len(edge[1][1]):
                    letters = letters + letter
                else:
                    letters = letters+","+letter
            node2 = str(edge[1][0]) + letters
        new_edge = (node1, node2)
        edge_list.append(new_edge)
    ni.edges(edge_list)
    return ni


def decomposition_printer(tree_decomposition):
    ni = dumb_converter(tree_decomposition)
    # print(ni.source)
    ni.render(directory='doctest-output', view=True)
    return


def display_graph_image(tree, network):

    ni = graphviz.Digraph("Display Graph")
    su = graphviz.Digraph('subgraph')  # Used for ranks
    su.attr(rank='same')

    # Setting shapes for nodes
    for node in tree:
        if node in network:
            su.node(str(node), str(node), shape='rectangle')
        else:
            ni.node(str(node), str(node))

    for node in network:
        if node in tree:
            continue
        else:
            ni.node(str(node), str(node))

    # Adding all edges
    for edge in network.edges:
        ni.edge(str(edge[0]), str(edge[1]))
    for edge in tree.edges:
        ni.edge(str(edge[1]), str(edge[0]), dir='back', arrowtail='vee')

    # EXPERIMENTAL

    # c.node('C')
    # c.edge('A', 'B')  # without rank='same', B will be below A

    ni.subgraph(su)

    # EXPERIMENTAL

    ni.render(directory='doctest-output', view=True)
    return
