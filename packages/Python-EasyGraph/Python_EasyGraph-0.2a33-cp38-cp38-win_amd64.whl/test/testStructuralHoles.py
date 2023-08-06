import sys
import networkx as nx
import matplotlib.pyplot as plt
sys.path.append('../')
import easygraph as eg
from networkx.algorithms.community import greedy_modularity_communities
# pass
def testHIS(G):
    c=eg.greedy_modularity_communities(G)
    for i in c:
        print(sorted(i))
    S,I,H = eg.get_structural_holes_HIS(G,c,epsilon = 0.01,weight = 'weight')
    print(S)
    print(I)
    print(H)
    print("-----------HIS-----------")
# pass
def testMAXD(G,k):
    c=eg.greedy_modularity_communities(G)
    node_list=eg.get_structural_holes_MaxD(G,k,c)
    print(node_list)
    print("-----------MAXD-----------")

# pass
def testCommonGreedy(G):
    node_list = eg.common_greedy(G,
              k = 2, # To find top three structural holes spanners.
              c = 1.0, # To define zeta: zeta = c * (n*n*n), and zeta is the large value assigned as the shortest distance of two unreachable vertices.
              weight = 'weight')
    print(node_list)
# pass
def testApGreedy(G):
    node_list = eg.AP_Greedy(G,
          k = 2, # To find top three structural holes spanners.
          c = 1.0, # To define zeta: zeta = c * (n*n*n), and zeta is the large value assigned as the shortest distance of two unreachable vertices.
          weight = 'weight')
    print(node_list)
    
# pass
def testEffectiveSize(G):
    result_dict = eg.effective_size(G,
               nodes=[1,2,3], # Compute the Effective Size of some nodes. The default is None for all nodes in G.
               weight='weight' # The weight key of the graph. The default is None for unweighted graph.
               )
    print(result_dict)
# pass
def testEfficiency(G):
    result_dict = eg.efficiency(G,
           nodes=[1,2,3], # Compute the Efficiency of some nodes. The default is None for all nodes in G.
           weight='weight' # The weight key of the graph. The default is None for unweighted graph.
           )
    print(result_dict)
# pass
def testConstraint(G):
    result_dict = eg.constraint(G,
           nodes=[1,2,3], # Compute the Constraint of some nodes. The default is None for all nodes in G.
           weight='weight', # The weight key of the graph. The default is None for unweighted graph.
           n_workers=4 # Parallel computing on four workers. The default is None for serial computing.
           )
    print(result_dict)

TG = nx.Graph()
G = eg.Graph()
G1 = eg.Graph()
karate_G = eg.Graph()
karate_TG = nx.karate_club_graph()

edges_1 = [(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (3, 6)]
edges_2 = [(5, 12), (6, 7), (7, 8), (7, 9), (7, 10), (7, 11), (11, 12)]

edges_3 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
edges_4 = [(5, 6), (5, 7), (6, 7)]
edges_5 = [(5, 1), (5, 2), (5, 3), (5, 4)]

G.add_edges(edges_1+edges_2)
G1.add_edges(edges_3+edges_4+edges_5)
karate_G.add_edges(list(karate_TG.edges()))
eg.get_structural_holes_HAM



'''
testHIS(G)
testMAXD(G,2)

c=len(eg.greedy_modularity_communities(G))
eg.get_structural_holes_HAM(G,2,c,
                         ground_truth_labels = [[0], [0], [0], [1], [1], [2], [2], [2], [2], [2], [1], [1]] ) 
print("-----------HAM-----------")
// output:
AMI
HAM: 0.7347541445436012
HAM_all: 0.2972338951098029
NMI
HAM: 0.8060059704030482
HAM_all: 0.4493519782744612
Entropy
HAM: 0.22493405784752332
HAM_all: 0.6044470678214261

c=len(eg.greedy_modularity_communities(G1))
eg.get_structural_holes_HAM(G1,2,c,
                         ground_truth_labels = [[0], [0], [0], [1], [1], [1], [1]] ) 
print("-----------HAM-----------")
// output:
AMI
HAM: 0.25126693574443504
HAM_all: 0.17895390044647513
NMI
HAM: 0.43253806776631243
HAM_all: 0.3156244234780851
Entropy
HAM: 0.38190850097688767
HAM_all: 0.48072261929232607


'''

''' ApGreedy + CommonGreedy
testApGreedy(G)
testCommonGreedy(G)
testApGreedy(G1)
testCommonGreedy(G1)
testApGreedy(karate_G)
testCommonGreedy(karate_G)
'''

''' EffectiveSize + constraint
TG.add_edges_from(edges_1+edges_2)
testEffectiveSize(G)
print("-----------------")
testEfficiency(G)
print("-----------------")
testConstraint(G)
print("-----------------")
print(nx.effective_size(TG))
print("-----------------")
print(nx.constraint(TG))
print("-----------------")
'''




