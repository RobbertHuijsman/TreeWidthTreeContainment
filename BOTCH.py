import networkx as nx
import ast
import time
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import BruteForce
import TreeDecomposition


def find_cherry(N, x):
    lst = list()
    for p in N.predecessors(x):
        if N.in_degree(p) == 1:
            for pc in N.successors(p):
                if pc != x:
                    t = N.out_degree(pc)
                    if t == 0:
                        lst.append((pc, x))
                    if t == 1:
                        for pcc in N.successors(pc):
                            if N.out_degree(pcc) == 0:
                                lst.append((pcc,x))
    return lst


def find_ret_cherry(N, x):
    lst = list()
    for p in N.predecessors(x):
        if N.out_degree(p) == 1:
            for pp in N.predecessors(p):
                for ppc in N.successors(pp):
                    if ppc != p:
                        if N.out_degree(ppc) == 0:
                            lst.append((x, ppc))
    return lst


def check_cherry(N, x, y):
    if N.has_node(x):
        if N.has_node(y):
            for px in N.predecessors(x):
                for py in N.predecessors(y):
                    if px == py:
                        return 1
                    if N.out_degree(px) == 1:
                        if px in N.successors(py):
                            return 2
    return False


def reduce_pair(N, x, y):
    k = check_cherry(N, x, y)
    if k == 1:
        for px in N.predecessors(x):
            N.remove_node(x)
            for ppx in N.predecessors(px):
                N.remove_node(px)
                N.add_edge(ppx,y)
            return True
    if k == 2:
        for px in N.predecessors(x):
            for py in N.predecessors(y):
                N.remove_edge(py,px)
                if N.in_degree(px) == 1:
                    for ppx in N.predecessors(px):
                        N.add_edge(ppx, x)
                        N.remove_node(px)
                #if N.out_degree(py) == 1:
                for ppy in N.predecessors(py):
                    N.add_edge(ppy, y)
                    N.remove_node(py)
                return True
    return False


def find_tcs(N):
    lst1 = list()
    for x in N.nodes():
        if N.out_degree(x) == 0:
            cherry1 = find_cherry(N,x)
            lst1.extend(cherry1)
    lst2 = list()
    while lst1:
        cherry = lst1.pop()
        k = check_cherry(N, cherry[0], cherry[1])
        if (k == 1) or (k == 2):
            reduce_pair(N, cherry[0], cherry[1])
            lst2.append(cherry)
            lst1.extend(find_cherry(N,cherry[1]))
            lst1.extend(find_ret_cherry(N,cherry[1]))
    return lst2


def cps_reduces_network(N, lst):
    for cherry in lst:
        reduce_pair(N, cherry[0], cherry[1])
    if N.size() == 1:
        return True
    return False


def tcn_contains(N, M):
    return cps_reduces_network(M, find_tcs(N))


def node_selector(network):
    """Picks nodes for the brute_foce_tree_child function."""
    for node in network:
        # Find reticulation
        if network.in_degree(node) != 2:
            continue
        # Find consecutive reticulations
        for parent in network.predecessors(node):
            # Reticulation node parent
            if network.in_degree(parent) != 2:
                continue
            # print(f"consecutive reticulation = {node} with parent {parent}")
            return node
        # Find sibling reticulations
        for parent in network.predecessors(node):
            # Tree node parent
            if network.out_degree(parent) != 2:
                continue
            for sibling in network.successors(parent):
                if sibling == node:
                    continue
                # Reticulation node sibling
                if network.in_degree(sibling) != 2:
                    continue
                # print(f"sibling reticulation = {node} with sibling {sibling}")
                return node

    # print(f"node = None")
    return None


def tc_brute_force(tree_in, network_in):

    todo_list = [network_in]

    reticulation_list = []
    for node in network_in:
        if network_in.in_degree(node) == 2:
            reticulation_list.append(node)

    while todo_list:
        network = todo_list.pop()

        node = node_selector(network)
        # print(f"node = {node}")
        if node is None:
            #     TreeDecomposition.display_graph_image(tree_in, network)
            tree = tree_in.copy()
            if tcn_contains(network, tree):
                return True

        else:
            for parent in network.predecessors(node):
                copy_network = network.copy()
                copy_network.remove_edge(parent, node)
                # print(f"removed edge {(parent, node)}")
                BruteForce.compact_node(copy_network, node)
                if copy_network.out_degree(parent) == 1:
                    BruteForce.compact_node(copy_network, parent)
                else:
                    # If the parent was a reticulation node before, we need to remove it entirely and fix its parents
                    fix_list = [parent]
                    while fix_list:
                        fix_node = fix_list.pop()
                        if copy_network.out_degree(fix_node) == 1:
                            BruteForce.compact_node(copy_network, fix_node)
                        else:
                            if fix_node not in copy_network:
                                # A node can be added to the list twice if both children are fixed. Just ignore it.
                                continue
                            for fix_parent in copy_network.predecessors(fix_node):
                                fix_list.append(fix_parent)
                            copy_network.remove_node(fix_node)

                todo_list.append(copy_network)
    return False
