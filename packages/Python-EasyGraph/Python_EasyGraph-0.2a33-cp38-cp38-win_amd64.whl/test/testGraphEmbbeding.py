import sys
import networkx as nx
import matplotlib.pyplot as plt
sys.path.append('../')
import easygraph as eg
from networkx.algorithms.community import greedy_modularity_communities


def testDeepWalk(G):
    skip_gram_params = dict( # The skip_gram parameters in Python package gensim.
         	window=10,
            min_count=1,
            batch_words=4,
            iter=15)
    return eg.deepwalk(G,
            dimensions=128, # The graph embedding dimensions.
            walk_length=80, # Walk length of each random walks.
            num_walks=10, # Number of random walks.
            **skip_gram_params
            )

def testNode2Vec(G):
    skip_gram_params=dict( # The skip_gram parameters in Python package gensim.
         	window=10,
            min_count=1,
            batch_words=4)
    eg.node2vec(G,
            dimensions=128, # The graph embedding dimensions.
            walk_length=80, # Walk length of each random walks.
            num_walks=10, # Number of random walks.
            p=1.0, # The `p` possibility in random walk in [2]
            q=1.0, # The `q` possibility in random walk in [2]
            weight_key=None,
            **skip_gram_params
            )

def testLINE(G):
    model = eg.LINE(G, 
             embedding_size=16, 
             order='all') # The order of model LINE. 'first'，'second' or 'all'.

    model.train(batch_size=1024, epochs=1, verbose=2)
    embeddings = model.get_embeddings() # Returns the graph embedding results.

def testSDNE(G):
    model = eg.SDNE(G, 
             hidden_size=[256, 128]) # The hidden size in SDNE.

    model.train(batch_size=3000, epochs=40, verbose=2)
    embeddings = model.get_embeddings() # Returns the graph embedding results.

G = eg.Graph()
TG = nx.Graph()
def generateGraph(G,TG,a,b,c,d):
    TG1 = nx.watts_strogatz_graph(a,4,0.3)
    TG2 = nx.watts_strogatz_graph(b,4,0.3)
    TG3 = nx.watts_strogatz_graph(c,4,0.3)
    TG4 = nx.watts_strogatz_graph(d,4,0.3)
    for (u,v) in TG1.edges():
        G.add_edge(u,v)
        TG.add_edges_from([(u,v)])
    for (u,v) in TG2.edges():
        G.add_edge(u+a,v+a)
        TG.add_edges_from([(u+a,v+a)])
    for (u,v) in TG3.edges():
        G.add_edge(u+a+b,v+a+b)
        TG.add_edges_from([(u+a+b,v+a+b)])
    for (u,v) in TG4.edges():
        G.add_edge(u+a+b+c,v+a+b+c)
        TG.add_edges_from([(u++a+b+c,v+a+b+c)])

generateGraph(G,TG,8,6,7,9)

#edges = list(TG1.edges())+list(TG2.edges())+list(TG3.edges())+list(TG4.edges())
#TG.add_edges_from(edges)
#TG.add_edges_from(list())
print(TG.edges())


nx.draw_circular(TG,with_labels=True)
plt.show()

# G.add_edges(list(TG.edges()))
# vec, nodes = testDeepWalk(G)
# print(vec)
# print(nodes)
