from demo.E.Dijkstra import sort_node
from demo.E.Vehicle import Vehicle

used_F = []
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
    Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']
    vehicles = phase3(Z_list)
    print(sum([veh.get_uncover_time() for veh in vehicles]) * 60)