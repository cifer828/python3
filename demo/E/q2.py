from itertools import combinations
from demo.E.Dijkstra import phase1
from demo.E.Dijkstra import sort_node
from demo.E.Dijkstra import phase3

def q2_brute():
    Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']
    new_Z = ['J25', 'J34', 'J36', 'J42', 'J49']
    combine_new_Z = list(combinations(new_Z, 2))
    result = []
    for cnZ in combine_new_Z:
        new_Z_list = Z_list + list(cnZ)
        vehicles = phase3(new_Z_list)
        total_uncover_time = sum([veh.get_uncover_time() for veh in vehicles])
        result.append([cnZ,total_uncover_time * 60])
    result = sorted(result, key = lambda  r : r[1])
    for r in result:
        print(r[0])
        print(round(r[1],1))
    return result

def q2_dist():
    phase1(['D1','D2'])
    new_Z = ['J25', 'J34', 'J36', 'J42', 'J49']
    for nZ in new_Z:
        dist_list = sort_node(nZ, 'F')
        dist = sum([dl[1] for dl in dist_list[:3]])
        print(nZ, round(dist, 1))

if __name__ == '__main__':
    # q2_dist()
    q2_brute()