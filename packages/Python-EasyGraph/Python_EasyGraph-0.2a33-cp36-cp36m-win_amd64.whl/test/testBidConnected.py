import sys
sys.path.append('../')
import easygraph as eg

G = eg.Graph()
DG = eg.DiGraph()


edges_1 = [(0, 6), (0, 1), (0, 2), (0, 5), (0, 4), (1, 5), (1, 3), (1, 4), (2, 4), (2, 5), (3, 6), (4, 5), (5, 6)]
edges_2 = [(7, 8), (8, 9), (9, 7)]
edges_3 = [(0, 7), (1, 7)]
edges_4 = [(0, 8)]
nodes_1 = [10, 11]
G.add_edges(edges_1)
# test is_connected(G)
print("is_biconnected: {}".format(eg.is_biconnected(G)))
print("connected_components: {}".format(eg.connected_components(G)))
print("generator_biconnected_components_nodes:")
for i in eg.generator_biconnected_components_nodes(G):
    print(i)
print("generator_biconnected_components_edges: {}".format(i))
for i in eg.generator_biconnected_components_edges(G):
    print(i)
print("generator_articulation_points: {}".format(i))
for i in eg.generator_articulation_points(G):
    print(i)
print("\n")

G.add_edges(edges_2)
print("is_biconnected: {}".format(eg.is_biconnected(G)))
print("connected_components: {}".format(eg.connected_components(G)))
print("generator_biconnected_components_nodes:")
for i in eg.generator_biconnected_components_nodes(G):
    print(i)
print("generator_biconnected_components_edges: ")
for i in eg.generator_biconnected_components_edges(G):
    print(i)
print("generator_articulation_points: ")
for i in eg.generator_articulation_points(G):
    print(i)
print("\n")

G.add_edges(edges_3)
print("is_biconnected: {}".format(eg.is_biconnected(G)))
print("connected_components: {}".format(eg.connected_components(G)))
print("generator_biconnected_components_nodes:")
for i in eg.generator_biconnected_components_nodes(G):
    print(i)
print("generator_biconnected_components_edges: ")
for i in eg.generator_biconnected_components_edges(G):
    print(i)
print("generator_articulation_points: ")
for i in eg.generator_articulation_points(G):
    print(i)
print("\n")

G.add_edges(edges_4)
print("is_biconnected: {}".format(eg.is_biconnected(G)))
print("connected_components: {}".format(eg.connected_components(G)))
print("generator_biconnected_components_nodes:")
for i in eg.generator_biconnected_components_nodes(G):
    print(i)
print("generator_biconnected_components_edges: ")
for i in eg.generator_biconnected_components_edges(G):
    print(i)
print("generator_articulation_points: ")
for i in eg.generator_articulation_points(G):
    print(i)
print("\n")

G.add_nodes(nodes_1)
print("is_biconnected: {}".format(eg.is_biconnected(G)))
print("connected_components: {}".format(eg.connected_components(G)))
print("generator_biconnected_components_nodes:")
for i in eg.generator_biconnected_components_nodes(G):
    print(i)
print("generator_biconnected_components_edges: ")
for i in eg.generator_biconnected_components_edges(G):
    print(i)
print("generator_articulation_points: ")
for i in eg.generator_articulation_points(G):
    print(i)
print("\n")

# test is_biconnected(G)
# test connected_components(G)
# test generator_biconnected_components_nodes(G)
# test generator_biconnected_components_edges(G)
# test generator_articulation_points(G)