import sys
sys.path.append('../')
import easygraph as eg

G = eg.Graph()
DG = eg.DiGraph()

D_edges_1 = [(0, 6), (0, 1), (0, 2), (0, 5), (1, 5), (1, 3), (3, 6), (4, 2), (4, 0), (4, 1), (5, 2), (5, 4), (6, 5)]
D_edges_2 = [(7, 8), (8, 9), (9, 7)]
D_nodes_1 = [10, 11]
DG.add_edges(D_edges_1)
# test is_connected(G)
print("is_connected: {}".format(eg.is_connected(DG)))
print("number_connected_components: {}".format(eg.number_connected_components(DG)))
DG.add_edges(D_edges_2)
DG.add_nodes(D_nodes_1)
# test is_connected(G)
print("is_connected: {}".format(eg.is_connected(DG)))
print("number_connected_components: {}".format(eg.number_connected_components(DG)))
print("connected_components: {}".format(eg.connected_components(DG)))
print("connected_component_of_node 0: {}".format(eg.connected_component_of_node(DG,0)))


edges_1 = [(0, 6), (0, 1), (0, 2), (0, 5), (0, 4), (1, 5), (1, 3), (1, 4), (2, 4), (2, 5), (3, 6), (4, 5), (5, 6)]
edges_2 = [(7, 8), (8, 9), (9, 7)]
nodes_1 = [10, 11]
G.add_edges(edges_1)
# test is_connected(G)
print("is_connected: {}".format(eg.is_connected(G)))
print("number_connected_components: {}".format(eg.number_connected_components(G)))
G.add_edges(edges_2)
G.add_nodes(nodes_1)
# test is_connected(G)
print("is_connected: {}".format(eg.is_connected(G)))
print("number_connected_components: {}".format(eg.number_connected_components(G)))
print("connected_components: {}".format(eg.connected_components(G)))
print("connected_component_of_node 0: {}".format(eg.connected_component_of_node(G,0)))

# test number_connected_components(G)
# test connected_components(G)
# test connected_component_of_node(G, node='Jack')
 


#G.add_edges_from_file("",weighted=True)
# # G.add_edges([(1,2), (2, 3)], edges_attr=[
# #     {
# #         'weight': 20
# #     },
# #     {
# #         'weight': 15
# #     }
# # ])
# # G.add_nodes(['Jack', 'Tom', 'Lily'], nodes_attr=[
# #     {
# #         'age': 10,
# #         'gender': 'M'
# #     },
# #     {
# #         'age': 11,
# #         'gender': 'M'
# #     },
# #     {
# #         'age': 10,
# #         'gender': 'F'
# #     }
# # ])
