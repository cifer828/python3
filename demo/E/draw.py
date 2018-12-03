from demo.E.Dijkstra import COORD_DICT
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from demo.E.Dijkstra import phase3

def draw_nx():
    G = nx.Graph()                 #建立一个空的无向图G
    pos = list(COORD_DICT.values())
    for line in open('adjacent_list.txt'):
        if len(line) < 1:
            break
        one_node = line.split()
        for i in range(1, len(one_node)):
            G.add_edge(one_node[0], one_node[i])
    nx.draw(G, pos=pos,  with_labels=True, font_size=10 ,font_color='white', edge_color='black', node_size=300, alpha=1)
    # plt.savefig("wuxiangtu.png")
    # print(G.node)
    plt.show()

def draw(phase):
    plt.figure(phase)
    main_road_list = ['J%02d' % (i+1) for i in range(20)]
    # 画边
    for line in open('adjacent_list.txt'):
        if len(line) < 1:
            break
        one_node = line.split()
        for i in range(1, len(one_node)):
            x, y = zip(COORD_DICT[one_node[0]], COORD_DICT[one_node[i]])
            if one_node[0] in main_road_list and one_node[i] in main_road_list:
                plt.plot(x, y, c=(0.2,0.2,0.2,0.2), lw='3')
            else:
                plt.plot(x, y, c=(0.2,0.2,0.2,0.2), lw='1')
    # 画点
    for node, coord in COORD_DICT.items():
        s = 20
        c = 'k'
        if 'F' in node:
            ms = 's'    # 矩形
        elif 'Z' in node:
            ms = 'D'    # 菱形
            c = 'g'
            s = 100
        elif 'D' in node:
            ms = '*'    # 五角星
            s = 200
            # c = 'y'
        elif 'J' in node:
            ms = 'o'    # 圆圈
        plt.scatter(coord[0], coord[1], marker=ms, c=c, s=s)
        plt.text(coord[0] + 1, coord[1] + 1, node)
    plt.show()

    # 解决方案的边
    Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']
    routes = phase3(Z_list)
    c_dict = {'A':'y', 'B':'b', 'C':'r'}    # 不同车型不同颜色
    for veh in routes:
        one_route = veh.route
        c = c_dict[veh.veh_type]
        if phase == 1:
            (start, end) = (1, veh.phase1_end)
            coord_s = COORD_DICT[veh.route[end - 1]]
            plt.scatter(coord_s[0], coord_s[1], marker='s', c=c, s=20)
            title = '第一阶段车辆调度图 待机地域-->转载地域'
        elif phase == 2:
            (start, end) = (veh.phase1_end, veh.phase2_end)
            title = '第二阶段车辆调度图 发射点位-->转载地域'
        elif phase == 3:
            title = '第三阶段车辆调度图 转载地域-->发射点位'
            (start, end) = (veh.phase2_end, len(one_route))
            coord_s = COORD_DICT[veh.route[-1]]
            plt.scatter(coord_s[0], coord_s[1], marker='s', c=c, s=20)
        # 相邻两节点连线
        for i in range(start, end):
            x, y = zip(COORD_DICT[one_route[i-1]], COORD_DICT[one_route[i]])
            # if one_route[i-1] in main_road_list and one_route[i] in main_road_list:
            #     plt.plot(x, y, c=c, lw='3')
            # else:
            plt.plot(x, y, c=c, lw='1')
        # 解决方案的点
    l_x = 220
    l_y = 15
    font = FontProperties(fname=r"c:\windows\fonts\msyh.ttc", size=10)    # 中文字体
    plt.plot([l_x,l_x+7], [l_y,l_y], c='y')
    plt.text(l_x+10, l_y - 2.5 ,'A类车', fontproperties=font)
    plt.plot([l_x,l_x+7], [l_y-5,l_y-5], c='b')
    plt.text(l_x+10, l_y - 7.5 ,'B类车', fontproperties=font)
    plt.plot([l_x,l_x+7], [l_y-10,l_y-10], c='r')
    plt.text(l_x+10, l_y - 12.5 ,'C类车', fontproperties=font)
    plt.xlim(0, 250)
    plt.ylim(0, 150)
    plt.title(title, fontproperties=font, fontsize = 16)
    plt.gcf().set_size_inches(12, 8)
    # plt.savefig('phase%d.png' % phase)
    plt.show()

if __name__ == '__main__':
    draw(1)
    # Z_list = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06']
    # vehicles = phase3(Z_list)
    # print(sum([veh.get_uncover_time() for veh in vehicles]) * 60)
    # for i in range(3):
    #     draw(i+1)