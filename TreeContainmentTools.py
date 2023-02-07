import networkx as nx
import graphviz


def path_searcher(signature, todo_node, go_down, embedding_path, path_list, initial_node):
    """This function searches a path"""
    print(f"path_searcher (todo_node = {todo_node}, go_down = {go_down}, embedding_path = {embedding_path}, path_list = {path_list}, initial_node = {initial_node})")
    if go_down:
        # Initializing:
        if initial_node is not None:
            print("Initializing")
            embedding_path = [(initial_node, todo_node)]
        else:
            embedding_path.append((embedding_path[-1][1], todo_node))

        # If there's enough space for a new edge  # TODO: is this check enough?
        if signature.network.in_degree(todo_node) + signature.network.out_degree(todo_node) < 3:
            # If its not a leaf:
            if todo_node not in signature.tree:
                return [embedding_path]
            else:
                return None
        else:
            for child in signature.network.successors(todo_node):
                # Check if the edge is still un-embedded
                success = False
                if (todo_node, child) not in signature.embedding.edge_dict.values():  # TODO: this is slow, use inverse embedding dict
                    extra_path = path_searcher(signature, child, go_down, embedding_path.copy(), [embedding_path.copy()], None)
                    if extra_path is not None:
                        path_list.extend(extra_path)
                        success = True
                else:
                    return None
                if success:
                    return path_list

    else:
        print(f"initial_node = {initial_node}")
        # Initializing:
        if initial_node is not None:
            print("Initializing")
            embedding_path = [(todo_node, initial_node)]
            print(f"embedding_path = {embedding_path}")
            if initial_node == 7 and len(signature.embedding.node_dict) == 6 and len(signature.network.nodes()) == 8:
                signature_image(signature, 99)

        else:
            print(f"TESTTEST embedding_path = {embedding_path}")
            signature_image(signature, 99)
            embedding_path.append((todo_node, embedding_path[1][0]))
            print(f"embedding_path = {embedding_path}")

        # If there's enough space for a new edge  # TODO: is this check enough?
        print(f"todo_node = {todo_node}")
        if todo_node == None:
            signature_image(signature, 99)
        if signature.network.in_degree(todo_node) + signature.network.out_degree(todo_node) < 3:
            # If its not a leaf:
            if todo_node not in signature.tree:
                return [embedding_path]
            else:
                return None
        else:
            for child in signature.network.successors(todo_node):
                # Check if the edge is still un-embedded
                if (todo_node, child) not in signature.embedding.edge_dict.values():  # TODO: this is slow, use inverse embedding dict
                    extra_path = path_searcher(signature, child, go_down, embedding_path.copy(), [embedding_path.copy()], None)
                    if extra_path is not None:
                        path_list.extend(extra_path)
                    return path_list
                else:
                    return None


def signature_image(signature, count):
    ni = graphviz.Digraph(str(count))
    # Setting colors and shapes for nodes
    for node in signature.tree:
        name = str(node)
        color = 'green'
        if signature.iso_labelling[node] == "FUTURE":
            color = 'blue'
        elif signature.iso_labelling[node] == "PAST":
            color = 'red'
        else:
            name = name + f" ({signature.iso_labelling[node]})"
        if node in signature.network:
            ni.node(str(node), name, shape='rectangle', color=color)
        else:
            ni.node(str(node), name, color=color)

    for node in signature.network:
        name = str(node)
        color = 'green'
        if signature.iso_labelling[node] == "FUTURE":
            color = 'blue'
        elif signature.iso_labelling[node] == "PAST":
            color = 'red'
        else:
            name = name + f" ({signature.iso_labelling[node]})"

        if node in signature.tree:
            continue
        else:
            if node in signature.embedding.inverse_node_dict:
                # ni.node(str(node), name, shape='triangle', color=color)
                # ni.node(str(node), name, fontname="times bold", color=color)
                ni.node(str(node), name, color=color)

            else:
                ni.node(str(node), name, color=color)
                # ni.node(str(node), name, shape='pentagon', color=color)

    # ni.node(signature.name, signature.name, shape='rectangle')  # TODO: debug feature

    # Adding all edges
    for edge in signature.network.edges:
        # Show embedded edges
        part_of_embedding = False
        for path in signature.embedding.edge_dict.values():
            if edge in path:
                part_of_embedding = True
        if part_of_embedding is True:
            ni.edge(str(edge[0]), str(edge[1]))
        else:
            ni.edge(str(edge[0]), str(edge[1]), arrowhead='empty')
    for edge in signature.tree.edges:
        ni.edge(str(edge[1]), str(edge[0]), dir='back', arrowtail='vee')

    ni.render(directory='doctest-output', view=True)
    return
