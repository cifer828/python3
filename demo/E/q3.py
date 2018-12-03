from itertools import combinations
from demo.E.Dijkstra import sort_node
from demo.E.Dijkstra import phase3
from demo.E.Vehicle import Vehicle
from demo.E.Dijkstra import used_F

def q3():
    '''
    去掉三阶段耗时最长的3辆车，替换为新车
    '''
    Z_list = ['Z01','Z02','Z03','Z04','Z05','Z06']
    vehicles = phase3(Z_list)
    sort_veh = sorted(vehicles, key = lambda v : v.time[-1] - v.get_uncover_time())
    del_veh = sorted([veh.num for veh in sort_veh[:3]])
    print(del_veh)
    vehicles = phase3(Z_list, del_list=del_veh)
    bazingga_J = ['J04','J06','J08','J13','J14','J15']  # 从天而降的车
    residual_F = ['F%02d'% (i + 1) for i in range(60) if 'F%02d'% (i + 1) not in used_F]    # 剩余F
    choices = []
    used_F2 = []
    bj_dist = []
    for bJ in bazingga_J:
        for rF in residual_F:
            test = sort_node(bJ, rF, 'C')
            one_pair = [bJ] + sort_node(bJ, rF, 'C')[:2]
            bj_dist.append(one_pair)
    bj_dist = sorted(bj_dist, key = lambda b : b[2])
    pass
    #     i = 0
    #     filled = 0
    #     while(True):
    #         # 避免重复
    #         if filled == 2:  # 一个点找两个F
    #             break
    #         if bJ_dist_2[i][0] not in used_F2:
    #             choices.append((bJ, i, bJ_dist_2[i][0], round(bJ_dist_2[i][1],2)))
    #             used_F2.append(bJ_dist_2[i][0])
    #             filled += 1
    #             i += 1
    #             continue
    #         # 寻找冲突F位置
    #         k = 0
    #         while(True):
    #             if bJ_dist_2[i][0] == choices[k][2]:
    #                 break
    #             k += 1
    #         # 新路径大于旧路径，更新新路径，否则采纳新路径，更新旧路径
    #         if bJ_dist_2[k][1] < choices[k][3]:
    #             choices.append((bJ, i, bJ_dist_2[i][0], round(bJ_dist_2[i][1], 2)))
    #             filled += 1
    #             old_dist = []
    #             for rF in residual_F:
    #                 old_dist += sort_node(choices[k][0], rF, 'C')
    #             pos = choices[k][1] + 1
    #             old_dist= sorted(old_dist, key = lambda b : b[1])
    #             while(old_dist[pos][0] in used_F2):
    #                 pos += 1
    #             new_F = old_dist[pos]
    #             choices.append((choices[k][0], pos, new_F[0], round(new_F[1],2)))
    #             del choices[k]
    #         i += 1
    # choices = sorted(choices, key = lambda  c : c[3])
    return choices

def q3_brute():
    Z_list = ['Z01','Z02','Z03','Z04','Z05','Z06']
    vehicles = phase3(Z_list)
    sort_veh = sorted(vehicles, key = lambda v : v.time[-1] - v.get_uncover_time())
    del_veh = sorted([veh.num for veh in sort_veh[:3]])
    # print(del_veh)
    bazingga_J = ['J04','J06','J08','J13','J14','J15','J04','J06','J08','J13','J14','J15']  # 从天而降的车
    combine_new_Z = list(combinations(bazingga_J, 3))
    j = 0
    result = []
    for cnZ in combine_new_Z:
        new_veh = []
        i = 100
        for v in cnZ:
            veh = Vehicle(v, 'C', i)
            veh.init_route([v])
            new_veh.append(veh)
            i += 1
        vehicles = phase3(Z_list, del_veh, new_veh)
        j += 1
        print(j)
        total_uncover_time = sum([veh.get_uncover_time() for veh in vehicles])
        r = (cnZ, total_uncover_time * 60)
        result.append(r)
        print(r)
    result = sorted(result,key = lambda x : x[1])
    with open('q3_brute.txt', 'w') as f:
        for r in result:
            f.write(r[0][0] + '\t' + r[0][1] + '\t'+ r[0][1] + '\t' + str(round(r[1],1)))
            f.write('\n')
    return result[:5]


if __name__ == '__main__':
    for q in q3():
        print(q)
    # print(q3_brute())
    # print(sort_node('J04', 'F01', 'C'))
