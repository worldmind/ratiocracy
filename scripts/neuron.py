import math

image_width = 800
image_height = 800

cfg = {
    'color': 'black',
    # x0, y0 - начало координат
    'x0': image_width//2,
    'y0': image_height//2,
    # Размер ядра нейрона 
    'nucleus_size': image_width//100,
    # Размер клетки
    'cell_size': image_width*4//100,
    # Высота ствола дендрита от начала координат
    'trunk_length': image_width//6,
    # Коэффициент для уменьшения высоты ветвей по отношению к предыдущему уровню 1/phi (золотое сечение)
    'branch_ratio': 1/1.618,
    # Коэффициент высоты корней относительно высоты ствола
    'root_ratio': 0.5,
    # Высота точки ветвления относительно длины ветви
    'mid_point_height_ratio': 0.1,
    # Число уровней ветвей, лучше в диапазоне от 4 до 6
    'depth': 4,
    # Число дендритов, лучше в диапазоне от 3 до 7, теоретический максимум 360/angular_width
    'tree_count': 5,
    # Количество ветвей из узла
    'branch_count': 2,
    # Начальный угол, 270 это отсчёт от вертикали
    'base_angle': 270,
    # Смещения узлов разных уровней относительно начального угла, подгоняются вручную
    'angles_shift': [],
    # Угловая толщина ствола в градусах
    'angular_width': 30,
    # Утолщение у основания
    'root_width_addon': 5,
    # Коэффициент уменьшения толщины ветвей относительно ствола, 1/e
    'thickness_ratio': 0.367879,
    # Вращать ли
    'rotate': True
}

for i in range(0, cfg['depth']+1):
    cfg['angles_shift'].append(0)

if cfg['rotate']:
    cfg['angles_shift'][1] = -(360/cfg['tree_count'])/3
    cfg['angles_shift'][2] = -(360/cfg['tree_count'])/5
    cfg['angles_shift'][3] = -(360/cfg['tree_count'])/10

    if cfg['tree_count'] == 5 and cfg['branch_count'] == 2:
        cfg['angles_shift'][1] = -25
        cfg['angles_shift'][2] = -12
        cfg['angles_shift'][3] = -4

levels_nodes = []
for i in range(0, cfg['depth']+1):
    levels_nodes.append(0)


def draw_arc(start_point, radius, end_point):
    print('<path d="M %d %d A %d %d %d %d %d %d %d" fill="none"/>' % (
            start_point[0],
            start_point[1],
            radius, radius,
            0, 0, 0,
            end_point[0],
            end_point[1]
            ))

def draw_line(start_point, end_point, color, name):
    delta = 0
    print('<path id="%s" d="M %d %d C %d %d %d %d %d %d" fill="none"/>' % (
            name,
            start_point[0], start_point[1],
            start_point[0]-delta, start_point[1]-delta,
            end_point[0]+delta, end_point[1]+delta,
            end_point[0], end_point[1]
            ))

def draw_tree(prev_left_point, prev_right_point, level, height, branch_height, max_nodes, angular_width, cfg):
    global levels_nodes
    if level == cfg['depth']:
        angle = cfg['base_angle'] + cfg['angles_shift'][level] - (360/max_nodes)*levels_nodes[level]
        x = cfg['x0'] + int(math.cos(math.radians(angle)) * height)
        y = cfg['y0'] + int(math.sin(math.radians(angle)) * height)
        leaf_point = (x, y)
        levels_nodes[level] += 1
        name = 'left:{}:{}'.format(level, levels_nodes[level])
        draw_line(prev_left_point, leaf_point, cfg['color'], name)
        name = 'right:{}:{}'.format(level, levels_nodes[level])
        draw_line(prev_right_point, leaf_point, cfg['color'], name)
    else:
        angular_half_width = angular_width/2
        angle = cfg['base_angle'] + cfg['angles_shift'][level] - (360/max_nodes)*levels_nodes[level]
        left_angle = angle - angular_half_width
        x = cfg['x0'] + int(math.cos(math.radians(left_angle)) * height)
        y = cfg['y0'] + int(math.sin(math.radians(left_angle)) * height)
        left_point = (x, y)
        name = 'left:{}:{}'.format(level, levels_nodes[level])
        draw_line(prev_left_point, left_point, cfg['color'], name)

        right_angle = angle + angular_half_width
        x = cfg['x0'] + int(math.cos(math.radians(right_angle)) * height)
        y = cfg['y0'] + int(math.sin(math.radians(right_angle)) * height)
        right_point = (x, y)

        name = 'right:{}:{}'.format(level, levels_nodes[level])
        draw_line(prev_right_point, right_point, cfg['color'], name)

        levels_nodes[level] += 1

        points = []
        angular_step = angular_width/cfg['branch_count']
        mid_angle = angle + angular_half_width - angular_step
        for i in range(1, cfg['branch_count']):
            x = cfg['x0'] + int(math.cos(math.radians(mid_angle)) * (height + branch_height*cfg['mid_point_height_ratio']))
            y = cfg['y0'] + int(math.sin(math.radians(mid_angle)) * (height + branch_height*cfg['mid_point_height_ratio']))
            points.append((x, y))
            mid_angle -= angular_step
        points.insert(0, right_point)
        points.append(left_point)

        for i in range(0,len(points)-1):
            draw_tree(points[i+1], points[i], level+1, height+branch_height*cfg['branch_ratio'], branch_height*cfg['branch_ratio'], max_nodes*cfg['branch_count'], angular_width*cfg['thickness_ratio'], cfg)



print('<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">' % (image_width, image_height))

print('<circle cx="%d" cy="%d" r="%d" stroke="%s" fill="none"/>' % (cfg['x0'], cfg['y0'],cfg['nucleus_size'], cfg['color']))
print('<circle cx="%d" cy="%d" r="%d" stroke="%s" fill="none"/>' % (cfg['x0'], cfg['y0'],cfg['cell_size'], cfg['color']))

print('<g id="neuron" stroke="%s" fill="white" stroke-width="1">' % (cfg['color']))

# Roots
start_point = ()
prev_point = ()
angle = cfg['base_angle'] + cfg['angles_shift'][0]
root_length = cfg['trunk_length']*cfg['root_ratio']
angular_half_width = cfg['root_width_addon'] + cfg['angular_width']/2
tree_angle = 360/cfg['tree_count']
for i in range(0,cfg['tree_count']):
    left_angle = angle - angular_half_width
    x = cfg['x0'] + int(math.cos(math.radians(left_angle)) * root_length)
    y = cfg['y0'] + int(math.sin(math.radians(left_angle)) * root_length)
    left_point = (x,y)

    right_angle = angle + angular_half_width
    x = cfg['x0'] + int(math.cos(math.radians(right_angle)) * root_length)
    y = cfg['y0'] + int(math.sin(math.radians(right_angle)) * root_length)
    right_point = (x, y)

    draw_tree(left_point, right_point, level=1, height=cfg['trunk_length'], branch_height=cfg['trunk_length']*cfg['branch_ratio'], max_nodes=cfg['tree_count'], angular_width=cfg['angular_width']*cfg['thickness_ratio'], cfg=cfg)

    if not start_point:
        start_point = right_point
    if prev_point:
        draw_arc(prev_point, root_length, right_point)
    prev_point = left_point

    angle = angle - tree_angle

draw_arc(prev_point, root_length, start_point)

print('</g>')
print('</svg>')
