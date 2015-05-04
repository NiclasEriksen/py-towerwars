import math
import random


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width//2
    image.anchor_y = image.width//2
    return image

def get_color(r, g, b, a):
    """ converts rgba values of 0 - 255 to the equivalent in 0 - 1 """
    return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)

def create_rectangle(cx, cy, w, h):
    rectangle = [
                cx - w // 2, cy - h // 2,
                cx - w // 2, cy + h // 2,
                cx + w // 2, cy + h // 2,
                cx + w // 2, cy - h // 2,
            ]
    return rectangle

def check_path(m, grid, new):
    update = False
    if new in m.path:
        if m.path.index(new) > m.point:
            update = True
            # if new == m.targetpoint:
            #     print("Tower placed at targetpoint.")
            #     m.targetpoint = m.currentpoint
            #     m.point -= 1
            #     m.currentpoint = m.lastpoint

    else:
        if m.targetpoint in m.path:
            for p in reversed(m.path):
                if m.path.index(p) >= m.path.index(m.targetpoint):
                    dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
                    ddirs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
                    for dir in dirs:
                        neighbor = (p[0] + dir[0], p[1] + dir[1])
                        if neighbor == new:
                            update = True
                            break
                    for dir in ddirs:
                        neighbor = (p[0] + dir[0], p[1] + dir[1])
                        if neighbor == new:
                            update = True
                            break

    return update


def get_diagonal(grid, x, y):
    diagonal_list = []
    ddirs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
    for dir in ddirs:
        neighbor = (x + dir[0], y + dir[1])
        if neighbor in grid:
            diagonal_list.append(neighbor)

    return diagonal_list


def get_neighbors(grid, x, y):
    neighbor_list = []
    dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    for dir in dirs:
        neighbor = (x + dir[0], y + dir[1])
        if neighbor in grid:
            neighbor_list.append(neighbor)

    return neighbor_list


def expandPath(grid, path):
    newpath = []
    for p in path:
        newpath.append(p)
        neighbors = get_neighbors(grid, p[0], p[1])
        diagonals = get_diagonal(grid, p[0], p[1])
        for d in diagonals:
            if not d in newpath:
                newpath.append(d)
        for n in neighbors:
            if not n in newpath:
                newpath.append(n)
    for n in newpath:
        if n[0] == 8:
            print(n)
    return newpath


def get_dist(x1, y1, x2, y2):  # Returns distance between to points
    x = (x1 - x2) * (x1 - x2)
    y = (y1 - y2) * (y1 - y2)
    dist = math.sqrt(x + y)
    return dist


def get_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    rads = math.atan2(-dy, dx)
    rads %= 2*math.pi
    return rads


def doDamage(a, t):
    if t.hp <= 0:
        t.state = "dead"
    else:
        if not a.cd:
            r = random.randint(1, 101)
            if r <= a.crit:
                t.hp -= a.dmg * 1.5
            else:
                t.hp -= a.dmg
            a.setCD(a.spd)
    return t
