import networkx as nx
import graphviz

ni = graphviz.Digraph("Flowchart")
su = graphviz.Digraph('subgraph')  # Used for ranks

su.node('True', 'Change x into a leaf', shape='ellipse')
su.node('False', 'Do not change x', shape='ellipse')
su.node('Uncertain', 'Uncertain', shape='ellipse')

# ni.node('1', 'Is x iso-labelled FUTURE?', shape='rectangle')
ni.node('2', 'Does x have iso-label FUTURE and out-degree 0?', shape='rectangle')
ni.node('3', '<Does the parent p<SUB>x</SUB> have an iso-label in S?>', shape='rectangle')
ni.node('4', '<Does &iota;(p<SUB>x</SUB>) have a leaf child in D(N, T)?>', shape='rectangle')
ni.node('5', '<Are all children of &iota;(p<SUB>x</SUB>) leaves in D(N, T)?>', shape='rectangle')
ni.node('51', '<Is the other child of p<SUB>x</SUB> a leaf?>', shape='rectangle')
ni.node('52', "<Does the other child of p<SUB>x</SUB> have a <BR/> FUTURE iso-label and outdegree-0?>", shape='rectangle')

ni.node('6', '<Does the parent p<SUB>&delta;(x)</SUB> of the <BR/> embedding &delta;(x) have an iso-label in S?>', shape='rectangle')
ni.node('7', '<Does &iota;(p<SUB>&delta;(x)</SUB>) have a leaf child in D(N, T)?>', shape='rectangle')
ni.node('8', '<Are all children of &iota;(p<SUB>&delta;(x)</SUB>) leaves in D(N, T)?>', shape='rectangle')
ni.node('9', '<Is the other child of p<SUB>&delta;(x)</SUB> a leaf?>', shape='rectangle')
ni.node('10', '<Is the other child of p<SUB>&delta;(x)</SUB> a <BR/> FUTURE iso-labelled embedding node <BR/> with indegree-1 and outdegree-0?>', shape='rectangle')

            # ni.node(str(node), name, fontname="times bold", color='red')
            # ni.node(str(node), name, shape='pentagon', color=color)


# Adding all edges
# ni.edge('1', '2', label=' Yes')
# ni.edge('1', 'False', label=' No')

ni.edge('2', '3', label=' Yes')
ni.edge('2', 'False', label=' No')

ni.edge('3', '4', label=' Yes')
ni.edge('3', '6', label=' No')

ni.edge('4', '5', label=' Yes')
ni.edge('4', 'False', label=' No')

ni.edge('5', 'True', label=' Yes')
ni.edge('5', '51', label=' No')

ni.edge('51', 'False', label=' Yes')
ni.edge('51', '52', label=' No')

ni.edge('52', 'Uncertain', label=' Yes')
ni.edge('52', 'True', label=' No')

ni.edge('6', '7', label=' Yes')
ni.edge('6', 'Uncertain', label=' No')

ni.edge('7', '8', label=' Yes')
ni.edge('7', 'Uncertain', label=' No')

ni.edge('8', 'True', label=' Yes')
ni.edge('8', '9', label=' No')

ni.edge('9', 'False', label=' Yes')
ni.edge('9', '10', label=' No')

ni.edge('10', 'Uncertain', label=' Yes')
ni.edge('10', 'True', label=' No')

su.attr(rank='same')
ni.subgraph(su)

# ni.edge('test1', 'test2', arrowhead='empty')

# ni.edge(str(edge[1]), str(edge[0]), dir='back', arrowtail='vee')

ni.render(directory='doctest-output', view=True)

