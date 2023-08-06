import sys
import cProfile
import pstats
from pstats import SortKey
import networkx as nx
import matplotlib.pyplot as plt

sys.path.append('../')
import easygraph as eg
from easygraph.functions.path import *

def testClosenessCentrality(G):
    print(eg.closeness_centrality(G))

def testBetweennessCentrality(G):
    print(eg.betweenness_centrality(G,weighted=False,normalized=True))

def testflowBetweennessCentrality(G):
    print(eg.flowbetweenness_centrality(G))

def testCentrality(G,TG):
    # if TG.is_directed()==True:
    #     print(nx.closeness_centrality(TG.reverse()))
    # else:
    #     print(nx.closeness_centrality(TG))
    print(nx.betweenness_centrality(TG))
    # testClosenessCentrality(G)
    testBetweennessCentrality(G)
    #print("--------------")

def test(G, TG):
    testCentrality(G, TG)
    #print(nx.second_order_centrality(TG))
    #print(nx.communicability_betweenness_centrality(TG))
    #print(eg.second_order_centrality(G))
    #print(eg.communicability_betweenness_centrality(G))
    #print(nx.group_betweenness_centrality(TG,[1,2]))
    #print(eg.group_betweenness_centrality(G,[1,2]))
    #print(nx.group_closeness_centrality(TG,[1,2]))
    #print(eg.group_closeness_centrality(G,[1,2]))
    #print(nx.group_degree_centrality(TG,[1,2]))
    #print(eg.group_degree_centrality(G,[1,2]))
    #print(nx.load_centrality(TG,weight="weight"))
    #print(eg.load_centrality(G))
    #print(nx.subgraph_centrality(TG))
    #print(eg.subgraph_centrality(G))
    #print(nx.harmonic_centrality(TG))
    #print(eg.harmonic_centrality(G))
    #print(nx.dispersion(TG))
    #print(eg.dispersion(G))
    #print(nx.global_reaching_centrality(TG,weight="weight"))
    #print(eg.global_reaching_centrality(G))
    #print(eg.global_reaching_centrality(G,weight="weight"))
    #print(nx.percolation_centrality(TG))
    
    
    
    
    
    
    

G=eg.Graph()
TG=nx.Graph()
#TG.add_edges_from([(4,5,{"weight":1}),(5,6,{"weight":1}),
#                (1,2,{"weight":1}),(2,3,{"weight":1}),(2,4,{"weight":1})])
TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":1}),(5,7,{"weight":1}),(6,7,{"weight":1}),
                (2,4,{"weight":1}),(1,5,{"weight":1}),(1,6,{"weight":1})])
print(TG.edges.data("weight"))
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
test(G,TG)

# centrality = nx.eigenvector_centrality(G)
# sorted( ( v, f"{c:0.2f}" )for v, c in centrality.items())
# centrality = nx.current_flow_closeness_centrality(TG)
# print(centrality)
# centrality = eg.current_flow_closeness_centrality(G)
# print(centrality)

'''
G=eg.Graph()
TG=nx.Graph()
TG.add_edges_from([(4,5,{"weight":1}),(5,6,{"weight":1}),(1,2,{"weight":1}),(2,3,{"weight":1}),(2,4,{"weight":1})])
print(TG.edges.data("weight"))
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
# centrality = nx.eigenvector_centrality(G)
# sorted( ( v, f"{c:0.2f}" )for v, c in centrality.items())
centrality = nx.current_flow_betweenness_centrality(TG)
print(centrality)
centrality = eg.current_flow_betweenness_centrality(G)
print(centrality)
'''


'''negative-weight edge pass!
G=eg.DiGraph()
TG=nx.DiGraph()
TG.add_edges_from([(1,2,{"weight":-1}),(2,3,{"weight":1}),(2,4,{"weight":1}),
    (7,5,{"weight":1}),(5,6,{"weight":1})])
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testCentrality(G,TG)
'''

''' no-point&no-edge、two-points&no-edge、graph with isolated point  pass!
G=eg.Graph()
TG=nx.Graph()
testCentrality(G,TG)

TG.add_nodes_from([7,8])
G.add_nodes([7,8])
testCentrality(G,TG)

TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":1}),(2,4,{"weight":1}),
    (2,5,{"weight":1}),(5,6,{"weight":1})])
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testCentrality(G,TG)
'''

'''disconnected graph pass!
G=eg.DiGraph()
TG=nx.DiGraph()
TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":1}),(2,4,{"weight":1}),
    (7,5,{"weight":1}),(5,6,{"weight":1})])
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testCentrality(G,TG)
'''
'''
# directed graph pass
TG = nx.DiGraph()
G = eg.DiGraph()  
TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":2}),(2,4,{"weight":1}),
    (2,5,{"weight":3}),(5,6,{"weight":4})])
print(TG.adj)
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
print(G.adj)

testCentrality(G,TG)

'''
''' different types pass!
TG = nx.Graph()
G = eg.Graph()  
TG.add_edges_from([(1,"lrc",{"weight":1}),("lrc",3,{"weight":2}),("lrc",4,{"weight":1}),
    (3,("tyy","lrc"),{"weight":3}),(("tyy","lrc"),6,{"weight":4})])
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testCentrality(G,TG)
'''

'''
G1=eg.Graph()
TG1=nx.Graph()
edges_1 = [(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (3, 6),(1,6)]
edges_2 = [(5, 12), (6, 7), (7, 8), (7, 9), (7, 10), (7, 11), (11, 12)]
G1.add_edges(edges_1)
TG1.add_edges_from(edges_1)
testCentrality(G,TG)
'''

''' big graph pass!
karate_TG = nx.karate_club_graph()
karate_G = eg.Graph()
karate_G.add_edges(list(karate_TG.edges()))
#testCentrality(karate_G,karate_TG)
#cProfile.run('testCentrality(karate_G,karate_TG)', 'restats')
print(karate_G.graph)
# p = pstats.Stats('restats')
# p.print_callees()
# p.add('restats')
#p.strip_dirs().sort_stats(-1).print_stats()
#SortKey.NAME、SortKey.CUMULATIVE、SortKey.TIME、SortKey.FILENAME
'''
# test flowbetweenness
''' not directed graph pass!
G=eg.Graph()
TG=nx.Graph()
TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":2}),(2,4,{"weight":1}),
    (2,5,{"weight":3}),(5,6,{"weight":4})])
print(TG.edges)
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testflowBetweennessCentrality(G)
'''
'''
G=eg.DiGraph()
TG=nx.DiGraph()
TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":2}),(2,4,{"weight":1}),
    (2,5,{"weight":3}),(5,6,{"weight":4})])
print(TG.edges)
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testflowBetweennessCentrality(G)
'''
'''
G=eg.DiGraph()
TG=nx.DiGraph()
TG.add_edges_from([(1,2,{"weight":2}),(1,3,{"weight":6}),(2,3,{"weight":1}),
    (2,4,{"weight":3}),(3,4,{"weight":3})])
print(TG.edges)
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testflowBetweennessCentrality(G)
'''
'''no-point&no-edge、two-points&no-edge、graph with isolated point、disconnected graph  pass!
G=eg.DiGraph()
TG=nx.DiGraph()
testflowBetweennessCentrality(G)
G.add_nodes([1,2])
testflowBetweennessCentrality(G)
TG.add_edges_from([(1,2,{"weight":2}),(1,3,{"weight":6}),(2,3,{"weight":1}),
    (2,4,{"weight":3}),(3,4,{"weight":3})])
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testflowBetweennessCentrality(G)
G.add_edges([(5,7),[6,5]],edges_attr=[
            {
                'weight': 1
            },
            {
                'weight': 1
            }
        ])
testflowBetweennessCentrality(G)
'''

'''different types pass!
G=eg.DiGraph()
TG=nx.DiGraph()
TG.add_edges_from([(("lrc","tyy"),"li",{"weight":2}),(("lrc","tyy"),3,{"weight":6}),("li",3,{"weight":1}),
    ("li",4,{"weight":3}),(3,4,{"weight":3})])
for (u, v, wt) in TG.edges.data('weight'):
    G.add_edge(u,v,weight=wt)
testflowBetweennessCentrality(G)
'''
