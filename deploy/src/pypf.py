DEBUG = False
#  from functions import get_neighbors


def neighbors(node, all_nodes, grid):
    dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    ddirs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
    result = []
    for dir in dirs:
        neighbor = (node[0] + dir[0], node[1] + dir[1])
        if neighbor in all_nodes:
            result.append(neighbor)
    for dir in ddirs:
        neighbor = (node[0] + dir[0], node[1] + dir[1])

        if neighbor in all_nodes:
            x, y = False, False
            for r in result:
                if neighbor[0]-1 == r[0] and neighbor[1] == r[1]:
                    x = True
                elif neighbor[0]+1 == r[0] and neighbor[1] == r[1]:
                    x = True
                if neighbor[1]-1 == r[1] and neighbor[0] == r[0]:
                    y = True
                elif neighbor[1]+1 == r[1] and neighbor[0] == r[0]:
                    y = True

            if y and x:
                if not neighbor in result:
                    result.append(neighbor)

    return result


def get_score(c, node, goal):
    score = c.score
    if c.node[0] != node[0] and c.node[1] != node[1]:
        score += 14
    else:
        score += 10

    gx = abs(goal[0] - c.node[0])
    gy = abs(goal[1] - c.node[1]) * 2
    score += (gx + gy) * 10
    return score


class Candidate:

    def __init__(self, node, lastnode=None):
        self.node = node
        self.score = 0
        self.visited = False
        self.lastnode = lastnode


def get_path(grid, all_nodes, node, goal):
    open_list = []
    closed_list = []
    path_list = []
    final_list = []
    start = node

    while node != goal:
        candidates = []

        for n in neighbors(node, all_nodes, grid):

            c = Candidate(n, node)
            candidates.append(c)

        for c in candidates:

            closed = False
            for cc in closed_list:
                if c.node == cc.node:
                    closed = True
            for co in open_list:
                if co.node == c.node:
                    closed = True

            if not closed:
                c.score = get_score(c, node, goal)

                open_list.append(c)

        # score_list = []
        # for c in open_list:
        #     score_list.append(c.score)

        # score_list.sort()

        # for s in score_list:
        #     for c in open_list:
        #         if c.score == s:
        #             c = c
        #             sorted_open_list.append(c)
        #             open_list.remove(c)

        open_list = sorted(
            open_list,
            key=lambda x: x.score,
            reverse=False
        )
        if len(open_list) > 0:
            next_c = open_list[0]
            closed_list.append(next_c)
            node = next_c.node
            open_list.remove(next_c)
        else:
            if DEBUG:
                print("Goal not found. Node {0} broke it.".format(node))
            break

    nextnode = goal
    for c in reversed(closed_list):
        if c.node == nextnode:
            path_list.append(c.node)
            nextnode = c.lastnode

    for c in reversed(path_list):
        final_list.append(c)

    if len(final_list) > 0:
        if DEBUG:
            print("Pathfinding successful!")
            print("Steps: {0}".format(len(final_list)))
        return final_list, True
    else:
        if DEBUG:
            print("ERROR: Pathfinding went wrong, returning to start.")
        final_list = [start]
        return final_list, False
