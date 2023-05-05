from os import path


def open_file(filename):
    with open(path.join(path.abspath('static/files'), filename), 'r') as file:
        data = file.read()
        split_data = data.split()
        num = int(split_data[0])
        del split_data[0]
        k = 0
        res = []
        for i in range(num):
            res.append([int(split_data[k]), int(split_data[k + 1]), int(split_data[k + 2]), int(split_data[k + 3])])
            k += 4
        res1 = [int(split_data[-4]), int(split_data[-3]), int(split_data[-2]), int(split_data[-1])]
        return res, res1


def open_file1(filename):
    with open(path.join(path.abspath('static/files'), filename), 'r') as file:
        data = file.readlines()
        num = int(data[0])
        del data[0]
        res = []
        for i in range(num+1):
            split_data = data[i].split()
            line = []
            temp = []
            for n in split_data:
                temp.append(int(n))
                if len(temp) == 2:
                    line.append((temp[-2], temp[-1]))
                    temp = []
            res.append(line)
        res1 = res[-1]
        del res[-1]
        return res, res1


def liang_barsky(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]

    u1 = 0
    u2 = 1

    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return None
            continue

        t = q[i] / p[i]

        if p[i] < 0:
            u1 = max(u1, t)
        else:
            u2 = min(u2, t)

        if u1 > u2:
            return None

    x1_new = x1 + u1 * dx
    y1_new = y1 + u1 * dy
    x2_new = x1 + u2 * dx
    y2_new = y1 + u2 * dy

    return x1_new, y1_new, x2_new, y2_new


def sutherland_hodgman(subject_polygon, clip_polygon):
    def inside(p, cp1, cp2):
        return (cp2[0] - cp1[0]) * (p[1] - cp1[1]) > (cp2[1] - cp1[1]) * (p[0] - cp1[0])

    def intersection(p1, p2, cp1, cp2):
        dc = [cp1[0] - cp2[0], cp1[1] - cp2[1]]
        dp = [p1[0] - p2[0], p1[1] - p2[1]]
        n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
        n2 = p1[0] * p2[1] - p1[1] * p2[0]
        n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
        return [(n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3]

    output = subject_polygon
    cp1 = clip_polygon[-1]

    for clip_vertex in clip_polygon:
        cp2 = clip_vertex
        input_list = output
        output = []
        s = input_list[-1]

        for subject_vertex in input_list:
            if inside(subject_vertex, cp1, cp2):
                if not inside(s, cp1, cp2):
                    output.append(intersection(s, subject_vertex, cp1, cp2))
                output.append(subject_vertex)
            elif inside(s, cp1, cp2):
                output.append(intersection(s, subject_vertex, cp1, cp2))
            s = subject_vertex
        cp1 = cp2

    return output
