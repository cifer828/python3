from demo.E.Dijkstra import sort_node
from demo.E.Dijkstra import dist
from demo.E.Dijkstra import COORD_DICT

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
