from itertools import combinations
import copy
from demo.E.Dijkstra import Dijkstra
from demo.E.Dijkstra import COORD_DICT
from demo.E.Dijkstra import dist
from demo.E.Dijkstra import read_adMat
from demo.E.Dijkstra import phase3
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import math

# 初始化图参数
# G = {1:{1:0,    2:1,    3:12},
#      2:{2:0,    3:9,    4:3},
#      3:{3:0,    5:5},
#      4:{3:4,    4:0,    5:13,   6:15},
#      5:{5:0,    6:4},
#      6:{6:0}}

Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']

def del_node(old_G, del_n, punish = 999):
    """
    :param old_G: 原图
    :param del_n: 删除节点，设所有与其直接相连的点距为99999
    :return: 返回删除节点后新图
    """
    new_G = copy.deepcopy(old_G)
    for key in new_G.keys():
        # 删除点为源点key，所有value设为999
        if key == del_n:
            for v_key in new_G[key].keys():
                new_G[key][v_key] += punish
    for value in new_G.values():
        for v in value.keys():
            if v == del_n:
                value[v] += punish
    return new_G

def Dijkstra_reciprocal(G, v0):
    """
    返回最短路径中各路径倒数之和，主干路权为2，其他路权为1
    """
    best_dist_dict, best_route_dict = Dijkstra(G, v0)
    # print('D_r')
    recip_sum = 0
    main_road_list = ['J%02d' % (i+1) for i in range(20)]
    # print(main_road_list)
    for route in best_route_dict.values():
        weighted_dist = 0
        for i in range(1, len(route)):
            weight= 1
            if route[i] in main_road_list and route[i-1] in main_road_list:
                weight = 0.5
            weighted_dist += weight * dist(COORD_DICT, route[i - 1], route[i])
        if weighted_dist != 0:
            recip_sum += 1.0 / weighted_dist
    return recip_sum



def q4(num):
    """
    单节点删除法评价节点重要性
    """
    G = read_adMat('D')
    J_list = [J for J in G.keys() if 'J' in J]   # 道路节点列表
    node_importance = sum([Dijkstra_reciprocal(G, J) for J in J_list])
    print(node_importance)
    del_J_combine = list(combinations(J_list, num))   # 选3个节点删除
    result = []
    i = 1
    for dJc in del_J_combine:
        new_G = copy.deepcopy(G)
        for del_J in dJc:
            new_G = del_node(new_G, del_J)
        new_node_importance = sum([Dijkstra_reciprocal(new_G, J) for J in J_list])
        diff = abs(round(node_importance - new_node_importance, 2))
        print(i)
        result.append([dJc, diff])
        i += 1

    result = sorted(result, key = lambda r : r[1], reverse = True)
    # 写入文件
    with open('q4_x%d.txt' % num, 'w') as f:
        f.write('initial importance : ' + str(node_importance))
        for r in result:
            for del_n in r[0]:
                f.write(del_n + '\t')
            f.write(str(r[1]) + '\n')
    return result


def q4_test():
    G = read_adMat('D')
    J = 'J02'
    print(J, Dijkstra_reciprocal(G, J))
    d1 = Dijkstra(G, 'J02')
    print(sum([1.0 / r for r in d1[0].values() if r != 0] ))
    new_G = del_node(del_node(G, J), J)
    d2 = Dijkstra(new_G, 'J02')
    print(sum([1.0 / r for r in d2[0].values() if r != 0]))

def q4_volume(vehicles):  # 第一问方案):
    # print(sum([veh.get_uncover_time() for veh in vehicles]) * 60) # 总暴露时间
    J_vol = dict(('J%02d' % (i + 1), 0) for i in range(62))
    for veh in vehicles:
        for node in veh.route:
            if 'J' in node:
                J_vol[node] += 1
    total_volume = sum(J_vol.values())
    for key in J_vol.keys():
        J_vol[key] = round(J_vol[key] /total_volume * 100, 2)
    # print(sum(J_vol.values()))
    return sorted(J_vol.items(), key = lambda item: item[1], reverse = True)

def draw_del_importance(flag):
    """
    问题四可视化
    1：删除节点法
    2：流量分析法
    """
    main_road_list = ['J%02d' % (i+1) for i in range(20)]
    # 画边
    for line in open('adjacent_list.txt'):
        if len(line) < 1:
            break
        one_node = line.split()
        for i in range(1, len(one_node)):
            x, y = zip(COORD_DICT[one_node[0]], COORD_DICT[one_node[i]])
            if one_node[0] in main_road_list and one_node[i] in main_road_list:
                plt.plot(x, y, c=(0.2,0.2,0.2,0.2), lw='2')
            else:
                plt.plot(x, y, c=(0.2,0.2,0.2,0.2), lw='1')
    # 画点
    if flag == 1:
        nodes = q4(1)
        for pair in nodes:
            node = pair[0][0]
            dist = pair[1]
            coord = COORD_DICT[node]
            plt.scatter(coord[0], coord[1], marker='o', c='r', s= dist * 50 + 10)
            plt.text(coord[0] + 1, coord[1] + 1, node)
        title = '删除节点法确定单节点重要性'
    elif flag == 2:
        nodes = q4_volume(phase3(Z_list))
        for pair in nodes:
            node = pair[0]
            dist = pair[1]
            coord = COORD_DICT[node]
            plt.scatter(coord[0], coord[1], marker='o', c='r', s= dist * 50 + 10)
            plt.text(coord[0] + 1, coord[1] + 1, node)
        title = '流量分析法确定单节点重要性'
    font = FontProperties(fname=r"c:\windows\fonts\msyh.ttc")    # 中文字体
    plt.title(title, fontproperties=font, fontsize = 24)
    plt.gcf().set_size_inches(12, 8)
    plt.savefig(title + '.png')
    # plt.show()

def q5(vehicles):
    # 信息熵
    nodes = q4_volume(vehicles)
    I = 0
    for n in nodes:
        if n[1] == 0:
            continue
        p =  n[1] / 100
        I -=  p * math.log(p, math.e)
    return round(I, 2)

def q5_punish(num):
    vehicles = phase3(Z_list)
    I_origin = q5(vehicles)
    total_time_origin = sum([veh.get_uncover_time() for veh in vehicles]) * 60
    punish_node = [node[0] for node in q4_volume(vehicles)]
    result = []
    for i in range(num):
        vehicles = phase3(Z_list, punish=punish_node[i], punish_time=10)
        I = q5(vehicles)
        if I < I_origin:
            I_final =2 * I_origin - I
        else:
            I_final = I
        total_time = sum([veh.get_uncover_time() for veh in vehicles]) * 60
        if total_time < total_time_origin:
            total_final = 2 * total_time_origin - total_time
        else:
            total_final = total_time
        result.append([punish_node[i], I_final, total_final])
    print(I_origin, total_time_origin)
    return result


if __name__ == '__main__':
    # print(q4(1))
    # for q in q4_volume():
    #     print(q)
    # draw_del_importance(1)
    # draw_del_importance(2)
    # print(q5(Z_list))
    for q5 in q5_punish(20):
        print(q5[0], round(q5[1],3), round(q5[2],1))