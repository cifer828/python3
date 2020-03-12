# Dijkstra算法——通过边实现松弛
# 指定一个点到其他各顶点的路径——单源最短路径
import math
from itertools import combinations
import copy
# 读取坐标
def read_coordinate():
    """
    读取坐标文件，返回各节点坐标
    """
    coordinate = dict()
    for line in open('zuobiao.txt'):
        if len(line) < 1:
            break
        line = line.split()
        coordinate[line[0]] = (int(line[1]), int(line[2]))
    return coordinate

COORD_DICT = read_coordinate()
used_F = [] # 已占用的发射站

def dist(coord_dict, point_a, point_b, veh_type = None):
    coord_a = coord_dict[point_a]
    coord_b = coord_dict[point_b]
    dist = math.sqrt((coord_a[0] - coord_b[0])**2 + (coord_a[1] - coord_b[1])**2)
    if veh_type == 'A':
        scale = 70 / 45
    elif veh_type == 'B':
        scale = 60 / 35
    elif veh_type == 'C':
        scale = 50 / 30
    else:
        scale = 1
    # 主干道距离按车速等效缩短
    if 'J' in point_a and 'J' in point_b:
        num_a = int(point_a[1:])
        num_b = int(point_b[1:])
        if abs(num_a - num_b) == 1 and num_a <= 20 and num_b <= 20:
            return dist/ scale
    return dist

def read_adMat(veh_type):
    """
    读取连接表，计算连接矩阵
    """
    adjacent_matrix = dict()
    coord_dict = COORD_DICT
    for line in open('adjacent_list.txt'):
        if len(line) < 1:
            break
        line = line.split()
        origin = line[0]
        adjacent_matrix[origin] = dict()
        for adjacent_point in line[1:]:
            adjacent_matrix[origin][adjacent_point] = dist(coord_dict, line[0], adjacent_point, veh_type)
    return adjacent_matrix

# 每次找到离源点最近的一个顶点，然后以该顶点为重心进行扩展
# 最终的到源点到其余所有点的最短路径
# 一种贪婪算法

def Dijkstra(G, v0, INF=9999):
    """ 使用 Dijkstra 算法计算指定点 v0 到图 G 中任意点的最短路径的距离
        INF 为设定的无限远距离值
        此方法不能解决负权值边的图
    """
    book = set()
    minv = v0

    # 源顶点到其余各顶点的初始路程
    dis = dict((v, INF) for v in G.keys())
    track = dict((v, [v]) for v in G.keys())
    dis[v0] = 0

    while len(book)<len(G):
        book.add(minv)                                  # 确定当期顶点的距离
        for w in G[minv]:                               # 以当前点的中心向外扩散
            if dis[minv] + G[minv][w] < dis[w]:         # 如果从当前点扩展到某一点的距离小与已知最短距离
                dis[w] = dis[minv] + G[minv][w]         # 对已知距离进行更新
                track[w] = track[minv] + [w]

        new = INF                                       # 从剩下的未确定点中选择最小距离点作为新的扩散点
        for v in dis.keys():
            if v in book: continue
            if dis[v] < new:
                new = dis[v]
                minv = v
    return dis,track

def sort_node(v0, ve, veh_type = 'D'):
    """
    从v0出发到各ve的最短路径，按距离排序
    v0: 出发地集合
    ve: 'F' 'Z'  'D'
    veh_type: 车型 ['A','B','C']
    """
    dis,track = Dijkstra(read_adMat(veh_type), v0)
    ascending_all = sorted(dis.items(), key = lambda item:item[1])  # 所有节点排序
    ascending_ve = [aa for aa in ascending_all if ve in aa[0] and aa[0] not in used_F ]    # 选择特定类型节点,去除使用过的发射基地
    routes = [[v[0], v[1], track[v[0]]] for v in ascending_ve]
    with open('phase1_dist_sort_%s-%s_%s.txt' % (v0, ve, veh_type), 'w') as f:
        for ve in ascending_ve:
            f.write(v0 + '-->' + ve[0] + ' ')
            f.write(str(ve[1]) + ' ')
            for node in track[ve[0]]:
                f.write('-->' + node)
            f.write('\n')
    return routes



class Vehicle:
    loc_daiji = ''
    veh_type = ''
    route = []
    time = []
    dist2z = []
    vel = {'A': 45, 'B': 35, 'C': 30}
    wait_in_Z = False
    phase1_end = 0
    phase2_end = 0
    cover_time = 0
    num = 0
    zhuanzai = ''
    def __init__(self, loc_daiji, veh_type, num):
        self.loc_daiji = loc_daiji
        self.veh_type = veh_type
        self.time = [0]
        self.num = num
    def init_route(self, route):
        """
        初始化各节点到达时刻
        """
        self.route = route
        for i in range(1, len(self.route)):
            self.time.append(dist(COORD_DICT, route[i - 1], route[i], self.veh_type) / self.vel[self.veh_type])
        for i in range(len(self.time) - 1, -1, -1):
            self.time[i] = sum(self.time[: i + 1])
        self.phase1_end = len(route)

    def edit_phase1_time(self, max_time):
        time = self.time[-1]
        for idx in range(len(self.time)):
            self.time[idx] += max_time - time

    def edit_phase23_time(self, max_time):
        time = self.time[-1]
        if self.wait_in_Z:
            self.cover_time = max_time - time
        else:
            self.cover_time = 1.0 / 6.0
        for idx in range(self.phase2_end, len(self.time)):
            self.time[idx] += self.cover_time

    def get_uncover_time(self):
        self.cover_time = self.time[self.phase2_end] - self.time[self.phase2_end - 1]
        return self.time[-1] - self.time[0] - self.cover_time

    def set_phase2_end(self, end):
        self.phase2_end = end
        self.zhuanzai = self.route[end - 1]

    def phase2_dist2Z(self, Z_list):
        self.dist2z = []
        for nz in Z_list:
            new_route = sort_node(self.route[-1], nz, self.veh_type)
            new_route[0][1] /= self.vel[self.veh_type]
            self.dist2z += new_route
        self.dist2z = sorted(self.dist2z, key = lambda r : r[1])

    def wait_for_pileup(self, wait_node, wait_time):
        # 同向冲突等待
        time = self.time[wait_node]
        node = self.route[wait_node]
        for node_num in range(wait_node, len(self.route)):
            self.time[node_num] += wait_time
        self.time.insert(wait_node, time)
        self.route.insert(wait_node, node)
        pass

    def phase1_wait_for_pileup(self, wait_node, wait_time):
        # 同向冲突等待
        for node_num in range(wait_node):
            self.time[node_num] += wait_time
        pass

    def add_route(self, route):
        old_num = len(self.route)
        self.route += route
        for i in range(len(route)):
            self.time.append(dist(COORD_DICT, self.route[i - 1 + old_num], self.route[i + old_num], self.veh_type) / self.vel[self.veh_type])
        for i in range(len(self.time) - 1, len(self.time) - len(route) - 1, -1):
            self.time[i] = sum(self.time[len(self.route) - len(route) - 1: i + 1])

    def get_end_node(self):
        return self.route[-1]


def phase1(start_nodes):
    """
    第一阶段：
    start_nodes: 出发节点，即待机基地
    """
    global used_F
    used_F = []
    veh_type = ['A', 'B', 'C']
    # 出发点至各发射地的最短距离词典
    dist_dict = dict(((node, vt),sort_node(node, 'F', vt)) for node in start_nodes for vt in veh_type)
    # 近点派慢车C，远点派快车A
    veh_routes = [] # 所有车最终路径
    num = 1
    for sn in start_nodes:
        for i in range(12):
            if i < 6:
                dist_list = dist_dict[(sn, 'C')]
                # 检查发射基地是否被先前车辆占用
                j = 0
                while(True):
                    if dist_list[j][0] not in used_F:
                        break
                    j = j + 1
                veh_route = Vehicle(sn, 'C', num)
                veh_route.init_route(dist_list[j][2])
                veh_routes.append(veh_route)
                used_F.append(veh_route.get_end_node())
                num += 1
            elif i < 9:
                dist_list = dist_dict[(sn, 'B')]
                j = 0
                while(True):
                    if dist_list[j][0] not in used_F:
                        break
                    j = j + 1
                veh_route = Vehicle(sn, 'B', num)
                veh_route.init_route(dist_list[j][2])
                veh_routes.append(veh_route)
                used_F.append(veh_route.get_end_node())
                num += 1
            elif i < 12:
                dist_list = dist_dict[(sn, 'A')]
                j = 0
                while(True):
                    if dist_list[j][0] not in used_F:
                        break
                    j = j + 1
                veh_route = Vehicle(sn, 'A', num)
                veh_route.init_route(dist_list[j][2])
                veh_routes.append(veh_route)
                used_F.append(veh_route.get_end_node())
                num += 1

    # 统一时间到达，反算出发时间
    max_time = max(v.time[-1] for v in veh_routes)
    # print(max_time)
    for v in veh_routes:
        v.edit_phase1_time(max_time)
    veh_routes = phase1_non_conflict(veh_routes)[0]
    return veh_routes

def deal_phase1_conflict(vehicle_routes):
    new_vehicle_routes, flag = phase1_non_conflict(vehicle_routes)
    while(flag):
        new_vehicle_routes, flag = phase1_non_conflict(new_vehicle_routes)
    return new_vehicle_routes


def phase1_non_conflict(vehicle_routes):
    '''
    phase1解决冲突
    '''
    # 每辆车
    flag = False
    for i_v in range(len(vehicle_routes)):
        # 目标车每个节点区间
        veh = vehicle_routes[i_v]
        for i_r in range(1, len(veh.route)):
            node_pair = (veh.route[i_r - 1], veh.route[i_r])    # 节点对
            time_pair = (veh.time[i_r - 1], veh.time[i_r])  # 时间对
            if node_pair[0] == node_pair[1] or i_r == len(veh.route):
                break
            # 比较其他车辆
            for i_other_v in range(i_v + 1, len(vehicle_routes)):
                other_veh = vehicle_routes[i_other_v]
                # 比较其他车辆每个节点
                for i_other_r in range(1, len(other_veh.route)):
                    other_node_pair = (other_veh.route[i_other_r - 1], other_veh.route[i_other_r])    # 节点对
                    other_time_pair = (other_veh.time[i_other_r - 1], other_veh.time[i_other_r])
                    # 同向冲突
                    if node_pair == other_node_pair:
                        if time_pair[0] < other_time_pair[0] and time_pair[1] > other_time_pair[1]:
                            other_veh.phase1_wait_for_pileup(i_other_r, time_pair[1] - other_time_pair[1])
                            # print('\nPhase1 Pileup')
                            # print(veh.num, node_pair, time_pair)
                            # print(other_veh.num, other_node_pair, other_time_pair)
                            flag = True
                            break
                        elif time_pair[0] > other_time_pair[0] and time_pair[1] < other_time_pair[1]:
                            veh.phase1_wait_for_pileup(i_r, other_time_pair[1] - time_pair[1])
                            # print('\nPhase1 Pileup')
                            # print(veh.num, node_pair, time_pair)
                            # print(other_veh.num, other_node_pair, other_time_pair)
                            flag = True
                            break
                    elif other_time_pair[0] > time_pair[1]: #　时间对超越并分离，退出循环
                        break
    return vehicle_routes, flag


def phase2(Z_list, del_list = None, new_veh =[]):
    """
    第二阶段
    """
    phase1_result = phase1(['D1', 'D2']) + new_veh
    for veh in phase1_result:
        veh.phase2_dist2Z(Z_list)
    sorted_routes = sorted(phase1_result, key = lambda x: x.num)
    if del_list:
        for del_l in del_list[::-1]:
            del sorted_routes[del_l - 1]
    sorted_routes = sorted(sorted_routes, key = lambda x: x.dist2z[0][1])
    # print(len(sorted_routes))
    # for sr in sorted_routes:
    #     print(sr.veh_type,sr.route[-1])
    #     for i in range(8):
    #         print(sr.dist2z[i][0:2])
    Z = dict((z, []) for z in Z_list)
    for veh in sorted_routes:
        best_Z = veh.dist2z[0][0] # 最优转载地域
        min = 0
        while(True):
            # 最近和次近的转载基地的最近发射基地列表
            z1_dist = sort_node(veh.dist2z[0][0], 'F', veh.veh_type)
            z2_dist = sort_node(veh.dist2z[1][0], 'F', veh.veh_type)
            # print(z1_dist, z2_dist)
            # 转载基地不足两辆车 or 到达转载基地的时间与前前一辆车相差超过10min
            # print(best_Z)
            if len(Z[best_Z]) < 2 or veh.dist2z[0][1] - Z[best_Z][-2][1] > 1.0 / 6.0:
                Z[best_Z].append((veh.route[-1], veh.dist2z[0][1]))
                break
            # 去第二近的转载基地花费时间 + 去转载基地最近发射基地时间 > 排队时间 + 去转载基地最近发射基地时间
            elif veh.dist2z[1][1] + z2_dist[0][1] > Z[best_Z][-2][1] + 1.0 / 6.0 + z1_dist[0][1]:
                Z[best_Z].append((veh.route[-1],  Z[best_Z][-2][1] + 1.0 / 6.0))    #　等待至前前辆车装载完毕
                break
            else:
                min += 1
                best_Z = veh.dist2z[min][0] # 更换第二近转载基地为目标基地

    for veh in sorted_routes:
        for zhuanzai, fashe in Z.items():
            for fs in fashe:
                if fs[0] == veh.route[-1]:
                    route_detail = sort_node(fs[0], zhuanzai, veh.veh_type)[0][2]
                    veh.add_route(route_detail[1:])
                    veh.set_phase2_end(len(veh.route))
                    break
    for key, value in Z.items():
        print(key, value)

    return sorted_routes, Z

def phase3(Z_list, del_list = None, new_veh = []):
    """
    第一阶段：
    start_nodes: 出发节点，即待机基地
    """
    global used_F
    sorted_routes, Z =  phase2(Z_list, del_list, new_veh)
    start_nodes = Z_list
    veh_type = ['A', 'B', 'C']
    # 出发点至各发射地的最短距离词典
    dist_dict = dict(((node, vt),sort_node(node, 'F', vt)) for node in start_nodes for vt in veh_type)
    for zi in start_nodes:
        # 从zi地出发的车辆集合
        veh_zi = [veh for veh in sorted_routes if veh.route[-1] == zi]
        sort_veh_zi = sorted(veh_zi, key = lambda x : x.time[-1], reverse = True)    # 后到的车去近处
        for i in range(len(sort_veh_zi)):
            veh = sort_veh_zi[i]
            if len(sort_veh_zi)- i < 3:
                veh.wait_in_Z = True
            dist_list = dist_dict[(zi, veh.veh_type)]
            # 检查发射基地是否被先前车辆占用
            j = 0
            while(True):
                if dist_list[j][0] not in used_F:
                    break
                j = j + 1
            veh.add_route(dist_list[j][2])
            used_F.append(veh.get_end_node())
    # 统一时间发射，反算从转载地出发时间
    max_time = max(v.time[-1] for v in sorted_routes) + 1.0 / 6.0
    # print(max_time)
    for v in sorted_routes:
        v.edit_phase23_time(max_time)
    return sorted_routes

def is_time_conflict(time_pair1, time_pair2):
    # 是否有对向冲突
    if time_pair1[0] > time_pair2[1] or time_pair1[1] < time_pair2[0]:
        return False
    return True

def is_time_pileup(time_pair1, time_pair2):
    # 是否有同向冲突
    if (time_pair1[0] < time_pair2[0] and time_pair1[1] > time_pair2[1]) or (time_pair1[0] > time_pair2[0] and time_pair1[1] < time_pair2[1]):
        return True
    return False

def non_conflict(vehicle_routes):
    '''
    解决冲突
    '''
    # 每辆车
    flag = False
    for i_v in range(len(vehicle_routes)):
        # 目标车每个节点区间
        veh = vehicle_routes[i_v]
        for i_r in range(1, len(veh.route)):
            node_pair = (veh.route[i_r - 1], veh.route[i_r])    # 节点对
            time_pair = (veh.time[i_r - 1], veh.time[i_r])  # 时间对
            if node_pair[0] == node_pair[1] or i_r == len(veh.route):
                break
            # 比较其他车辆
            for i_other_v in range(i_v + 1, len(vehicle_routes)):
                other_veh = vehicle_routes[i_other_v]
                # 比较其他车辆每个节点
                for i_other_r in range(1, len(other_veh.route)):
                    other_node_pair = (other_veh.route[i_other_r - 1], other_veh.route[i_other_r])    # 节点对
                    other_time_pair = (other_veh.time[i_other_r - 1], other_veh.time[i_other_r])
                    # 对向冲突
                    if node_pair == other_node_pair[::-1] and is_time_conflict(time_pair, other_time_pair):
                        print('\nConflict')
                        print(veh.num, node_pair, time_pair)
                        print(other_veh.num, other_node_pair, other_time_pair)
                        flag = True
                        break
                    # 同向冲突
                    if node_pair == other_node_pair:
                        if time_pair[0] < other_time_pair[0] and time_pair[1] > other_time_pair[1]:
                            other_veh.wait_for_pileup(i_other_r, time_pair[1] - other_time_pair[1])
                            # print('\nPileup')
                            # print(veh.num, node_pair, time_pair)
                            # print(other_veh.num, other_node_pair, other_time_pair)
                            flag = True
                            break
                        elif time_pair[0] > other_time_pair[0] and time_pair[1] < other_time_pair[1]:
                            veh.wait_for_pileup(i_r, other_time_pair[1] - time_pair[1])
                            # print('\nPileup')
                            # print(veh.num, node_pair, time_pair)
                            # print(other_veh.num, other_node_pair, other_time_pair)
                            flag = True
                            break
                    elif other_time_pair[0] > time_pair[1]: #　时间对超越并分离，退出循环
                        break
    return vehicle_routes, flag

# for veh in phase1(['D1', 'D2']):
#     print(veh.loc_daiji, veh.veh_type)
#     print(veh.route)
#     print(veh.time)
# print(used_F)

# for veh in phase2(['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06'])[0]:
#     print(veh.loc_daiji, veh.veh_type)
#     print(veh.route)
#     print(veh.time)
# for key, value in phase2(11)[1].items():
#     print(key, value)

# vehicles = phase3()
# for veh in vehicles:
#     print(veh.num, veh.loc_daiji, veh.veh_type, veh.wait_in_Z, veh.get_uncover_time())
#     print(veh.route)
#     print(veh.time)

def deal_conflict(vehicle_routes):
    new_vehicle_routes, flag = non_conflict(vehicle_routes)
    return new_vehicle_routes

# vehicles = deal_conflict(phase3())
# for veh in vehicles:
#     print(veh.num, veh.loc_daiji, veh.veh_type, veh.wait_in_Z, veh.get_uncover_time())
#     print(veh.route)
#     print(veh.time)
#     print()

def output(filename):
    # Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']     # 第一问初始
    Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06', 'J25', 'J34', 'J36', 'J42', 'J49']  # 第二问初始
    # Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06','J25','J34'] # 第二问第一种解法结果
    vehicles = phase3(Z_list)
    result = sorted(vehicles, key = lambda v : v.num)
    for veh in result:
        print(veh.num, veh.loc_daiji, veh.veh_type, veh.zhuanzai, veh.get_uncover_time() * 60)
        print(veh.route)
        print(veh.time)
        print('\n')
    with open(filename, 'w') as f:
        for veh in result:
            uct = veh.get_uncover_time()
            # print(round(veh.cover_time * 60,1))
            print(round(uct * 60,1))
            f.write(str(veh.num) + '\t'+ veh.veh_type + '\t' + veh.loc_daiji + '\t')
            for i in range(len(veh.route)):
                f.write(veh.route[i] + '\t' + str(round(veh.time[i] * 60,1)) + '\t' + str(round(veh.time[i] * 60,1)) + '\t')
            f.write('\n')
    # new_result = sorted(vehicles, key = lambda v : v.get_uncover_time())
    # for nr in new_result:
    #     print(nr.num, nr.get_uncover_time(), nr.veh_type, nr.zhuanzai)

# output('q2.txt')

def q2_brute():
    Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']
    new_Z = ['J25', 'J34', 'J36', 'J42', 'J49']
    combine_new_Z = list(combinations(new_Z, 2))
    for cnZ in combine_new_Z:
        new_Z_list = Z_list + list(cnZ)
        vehicles = phase3(new_Z_list)
        total_uncover_time = sum([veh.get_uncover_time() for veh in vehicles])
        print(new_Z_list)
        print(total_uncover_time * 60)

def q2_dist():
    phase1(['D1','D2'])
    new_Z = ['J25', 'J34', 'J36', 'J42', 'J49']
    for nZ in new_Z:
        dist_list = sort_node(nZ, 'F')
        dist = sum([dl[1] for dl in dist_list[:3]])
        print(nZ, dist)


def q3():
    '''
    去掉三阶段耗时最长的3辆车，替换为新车
    '''
    Z_list = ['Z01','Z02','Z03','Z04','Z05','Z06']
    vehicles = phase3(Z_list)
    sort_veh = sorted(vehicles, key = lambda v : v.time[-1] - v.cover_time, reverse = True)
    for sv in sort_veh:
        print(sv.num, round((sv.time[-1] - sv.cover_time - 2.97) * 60, 1))
    del_veh = sorted([veh.num for veh in sort_veh[:3]])
    vehicles = phase3(Z_list, del_list=del_veh)
    bazingga_J = ['J04','J06','J08','J13','J14','J15']  # 从天而降的车
    residual_F = ['F%02d'% (i + 1) for i in range(60) if 'F%02d'% (i + 1) not in used_F]    # 剩余F
    choices = []
    used_F2 = []
    bj_dist = []
    for bJ in bazingga_J:
        for rF in residual_F:
            test = sort_node(bJ, rF, 'C')
            one_pair = [bJ] + sort_node(bJ, rF, 'C')[0][:2]
            bj_dist.append(one_pair)
    bj_dist = sorted(bj_dist, key = lambda b : b[2])
    J_count = dict((bJ, 0) for bJ in bazingga_J)
    del_list = []
    for idx in range(len(bj_dist)):
        if J_count[bj_dist[idx][0]] == 2:
            del_list.append(idx)
            continue
        elif bj_dist[idx][1] not in used_F2:
            used_F2.append(bj_dist[idx][1])
            J_count[bj_dist[idx][0]] += 1
        else:
            del_list.append(idx)
    for i in del_list[::-1]:
        del bj_dist[i]
    return bj_dist

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

#
# for q in q3():
#     print(q)
# print(q3_brute())


# q2_dist()
# q2_brute()

# output('q2_zhuanzai_compare')

# 初始化图参数
# G = {1:{1:0,    2:1,    3:12},
#      2:{2:0,    3:9,    4:3},
#      3:{3:0,    5:5},
#      4:{3:4,    4:0,    5:13,   6:15},
#      5:{5:0,    6:4},
#      6:{6:0}}

def del_node(old_G, del_n):
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
                new_G[key][v_key] = 999
    for value in new_G.values():
        for v in value.keys():
            if v == del_n:
                value[v] = 999
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


def q4_test():
    G = read_adMat('D')
    J = 'J02'
    print(J, Dijkstra_reciprocal(G, J))
    d1 = Dijkstra(G, 'J02')
    print(sum([1.0 / r for r in d1[0].values() if r != 0] ))
    new_G = del_node(del_node(G, J), J)
    d2 = Dijkstra(new_G, 'J02')
    print(sum([1.0 / r for r in d2[0].values() if r != 0]))

def q2_new():
    J_list = ['J25', 'J34', 'J36', 'J42', 'J49']
    for J in J_list:
        r = sort_node('F47', J, 'C')
        print(r)


# q2_new()
# print(del_node(G, 1))
# q4(3)
# q4_test()
print(dist(COORD_DICT,'J11', 'J10') * 60/50)