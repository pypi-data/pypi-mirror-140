# import cProfile
# import re
# import easygraph as eg
# import pstats
# from pstats import SortKey

# G = eg.datasets.get_graph_karateclub()
# # community = eg.LPA(G)
# community = {1: [25, 23, 28, 9, 24, 15, 30, 33, 29, 32, 31, 34, 16, 21, 27, 19, 26], 2: [17, 6, 11, 7, 5], 3: [22, 4, 8, 10, 2, 20, 18, 12, 1, 3, 13, 14]}
# print(community)
# fcommunity = []
# for i, j in community.items():
#     fcommunity.append(frozenset(j) )
# print(fcommunity) 

# def test(one,two):
#     print(one,two)

# cProfile.runctx("eg.get_structural_holes_HIS(G,fcommunity)", globals(), locals(),'restats' )
# #cProfile.runctx("test(1,2)", globals(), locals(),'restats' )

# p = pstats.Stats('restats')
# p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
def fibonacci():
    a, b = (0, 1)
    while True:
        yield a
        a, b = b, a+b

fibos = fibonacci()
print(next(fibos)) #=> 0
next(fibos) #=> 1
next(fibos) #=> 1
next(fibos) #=> 2
