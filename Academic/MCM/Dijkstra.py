# Dijkstra算法——通过边实现松弛
# 指定一个点到其他各顶点的路径——单源最短路径
import math

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

def dist(coord_dict, point_a, point_b, veh_type = None, punish = None, punish_time = 5):
    coord_a = coord_dict[point_a]
    coord_b = coord_dict[point_b]
    dist = math.sqrt((coord_a[0] - coord_b[0])**2 + (coord_a[1] - coord_b[1])**2)
    if point_a == punish or point_b == punish:
        dist += punish_time   # 惩罚加5公里
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

def read_adMat(veh_type, punish = None, punish_time = 5):
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
            adjacent_matrix[origin][adjacent_point] = dist(coord_dict, line[0], adjacent_point, veh_type, punish, punish_time)
    return adjacent_matrix

# 每次找到离源点最近的一个顶点，然后以该顶点为重心进行扩展
# 最终的到源点到其余所有点的最短路径
# 一种贪婪算法

def Dijkstra(G, v0, INF=9999):
    """ 使用 E 算法计算指定点 v0 到图 G 中任意点的最短路径的距离
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

def sort_node(v0, ve, veh_type = 'D',punish = None, punish_time = 5 ):
    """
    从v0出发到各ve的最短路径，按距离排序
    v0: 出发地集合
    ve: 'F' 'Z'  'D'
    veh_type: 车型 ['A','B','C']
    """

    dis,track = Dijkstra(read_adMat(veh_type, punish, punish_time), v0 )
    ascending_all = sorted(dis.items(), key = lambda item:item[1])  # 所有节点排序
    ascending_ve = [aa for aa in ascending_all if ve in aa[0] and aa[0] not in used_F ]    # 选择特定类型节点,去除使用过的发射基地
    routes = [[v[0], v[1], track[v[0]]] for v in ascending_ve]
    # with open('phase1_dist_sort_%s-%s_%s.txt' % (v0, ve, veh_type), 'w') as f:
    #     for ve in ascending_ve:
    #         f.write(v0 + '-->' + ve[0] + ' ')
    #         f.write(str(ve[1]) + ' ')
    #         for node in track[ve[0]]:
    #             f.write('-->' + node)
    #         f.write('\n')
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

    def get_uncover_time(self, max_time = 8.28):
        self.cover_time = self.time[self.phase2_end] - self.time[self.phase2_end - 1]
        return max_time - self.time[0] - self.cover_time

    def set_phase2_end(self, end):
        self.phase2_end = end
        self.zhuanzai = self.route[end - 1]

    def phase2_dist2Z(self, Z_list):
        self.dist2z = []
        for nz in Z_list:
            new_route = sort_node(self.route[-1], nz, self.veh_type, )
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

def phase1(start_nodes, punish = None, punish_time = 5 ):
    """
    第一阶段：
    start_nodes: 出发节点，即待机基地
    """
    global used_F
    used_F = []
    veh_type = ['A', 'B', 'C']
    # 出发点至各发射地的最短距离词典
    dist_dict = dict(((node, vt),sort_node(node, 'F', vt, punish, punish_time)) for node in start_nodes for vt in veh_type)
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


def phase2(Z_list, del_list = None, new_veh =[], punish = None, punish_time = 5 ):
    """
    第二阶段
    """
    phase1_result = phase1(['D1', 'D2'], punish , punish_time) + new_veh
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
            z1_dist = sort_node(veh.dist2z[0][0], 'F', veh.veh_type, punish , punish_time)
            z2_dist = sort_node(veh.dist2z[1][0], 'F', veh.veh_type, punish , punish_time)
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
                    route_detail = sort_node(fs[0], zhuanzai, veh.veh_type, punish , punish_time)[0][2]
                    veh.add_route(route_detail[1:])
                    veh.set_phase2_end(len(veh.route))
                    break
    return sorted_routes, Z

def phase3(Z_list, del_list = None, new_veh = [], punish=None , punish_time=5):
    """
    第一阶段：
    start_nodes: 出发节点，即待机基地
    """
    global used_F
    sorted_routes, Z =  phase2(Z_list, del_list, new_veh, punish , punish_time)
    start_nodes = Z_list
    veh_type = ['A', 'B', 'C']
    # 出发点至各发射地的最短距离词典
    dist_dict = dict(((node, vt),sort_node(node, 'F', vt, punish , punish_time)) for node in start_nodes for vt in veh_type)
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

def deal_conflict(vehicle_routes):
    new_vehicle_routes, flag = non_conflict(vehicle_routes)
    return new_vehicle_routes

def output(filename):
    Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']     # 第一问初始
    # Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06', 'J25', 'J34', 'J36', 'J42', 'J49']  # 第二问初始
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

if __name__ == '__main__':
    # Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']
    # vehicles = phase3(Z_list)
    print(len('A2C89B278CEB9FD43DAF0916C3BCBD75'))
    # vehicles = sorted(vehicles, key = lambda x:x.num)
    # for veh in vehicles:
    #     print(veh.num, round((veh.get_uncover_time() * 60), 1))
    # print(sum([veh.get_uncover_time() for veh in vehicles]) * 60)
    # for veh in vehicles:
    #     time0 = round(veh.time[0] * 60, 1)
    #     time1 = round(veh.time[veh.phase1_end - 1] * 60, 1)
    #     time2 = round(veh.time[veh.phase2_end - 1] * 60, 1)
    #     time3 = round(veh.time[veh.phase2_end] * 60, 1)
    #     time4 = round(veh.time[-1] * 60, 1)
    #     print(veh.num, '\t', veh.veh_type, '\t', veh.route[0], '\t', round((time1 - time0), 1), '\t', round((time2 - time1), 1), '\t', round((497 - time3), 1))



