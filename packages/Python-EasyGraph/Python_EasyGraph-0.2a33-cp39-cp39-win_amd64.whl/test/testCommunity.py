import sys
import networkx as nx
sys.path.append('../')
import easygraph as eg
from networkx.algorithms.community import greedy_modularity_communities

def testCommunity(G,TG):
    c=list(eg.greedy_modularity_communities(G))
    for i in c:
        print(sorted(i))
    c=list(greedy_modularity_communities(TG))
    for i in c:
        print(sorted(i))
    print("-----------------------------")

''' no-point&no-edge、two-points&no-edge、graph with isolated point  pass!
G=eg.Graph()
TG=nx.Graph()
#testCommunity(G,TG)

TG.add_nodes_from([7,8])
G.add_nodes([7,8])
#testCommunity(G,TG)

TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":1}),(2,4,{"weight":1}),
    (2,5,{"weight":1}),(5,6,{"weight":1})])
G.add_edges(list(TG.edges()))
testCommunity(G,TG)
'''

''' disconnected graph pass!
G=eg.Graph()
TG=nx.Graph()
TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":1}),(2,4,{"weight":1}),
    (7,5,{"weight":1}),(5,6,{"weight":1})])
G.add_edges(list(TG.edges()))
testCommunity(G,TG)
'''

''' directed graph pass
TG = nx.DiGraph()
G = eg.DiGraph()  
TG.add_edges_from([(1,2,{"weight":1}),(2,3,{"weight":2}),(2,4,{"weight":1}),
    (2,5,{"weight":3}),(5,6,{"weight":4})])
G.add_edges(list(TG.edges()))
testCommunity(G,TG)

testflowBetweennessCentrality(G)
'''
''' different types pass!
TG = nx.Graph()
G = eg.Graph()  
TG.add_edges_from([(1,"lrc",{"weight":1}),("lrc",3,{"weight":2}),("lrc",4,{"weight":1}),
    (3,("tyy","lrc"),{"weight":3}),(("tyy","lrc"),6,{"weight":4})])
G.add_edges(list(TG.edges()))
testCommunity(G,TG)
'''

'''
G1=eg.Graph()
TG1=nx.Graph()
edges_1 = [(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (3, 6),(1,6)]
edges_2 = [(5, 12), (6, 7), (7, 8), (7, 9), (7, 10), (7, 11), (11, 12)]
G1.add_edges(edges_1)
TG1.add_edges_from(edges_1)
testCommunity(G,TG)
'''

''' big graph pass!
karate_TG = nx.karate_club_graph()
karate_G = eg.Graph()
karate_G.add_edges(list(karate_TG.edges()))
testCommunity(karate_G,karate_TG)
'''
