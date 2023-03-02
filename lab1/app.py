import json
import logging

from flask import Flask, render_template, request

app = Flask(__name__)

# Default values
white = [95.047, 100.0, 108.883]

logging.basicConfig(filename='backend.log', level=logging.DEBUG)


def lab_helper(x):
    res = 0
    if x >= 0.008856:
        res = x ** (1 / 3)
    else:
        res = (7.787 * x) + (16 / 116)
    return res


def xyz_to_rgb_helper(x):
    res = 0
    if x >= 0.0031308:
        res = (1.055 * (x ** (1 / 2.4))) - 0.055
    else:
        res = 12.92 * x
    return res


def one_more_xyz_to_rgb(x):
    res = 0
    if x >= 0.04045:
        res = ((x + 0.055) / 1.055) ** 2.4
    else:
        res = x / 12.92
    return res


def all_to_rgb(code: list, model: str) -> list:
    res = [0, 0, 0]

    for i in range(len(code)):
        code[i] = float(code[i])

    if model == 'cmyk':
        res[0] = 255 * (1 - code[0]) * (1 - code[3])
        res[1] = 255 * (1 - code[1]) * (1 - code[3])
        res[2] = 255 * (1 - code[2]) * (1 - code[3])
        return res

    if model == 'xyz':
        code[0], code[1], code[2] = code[0]/100, code[1]/100, code[2]/100
        rn = 3.2404542 * code[0] - 1.5371385 * code[1] - 0.4985314 * code[2]
        gb = -0.9692660 * code[0] + 1.8760108 * code[1] + 0.0415560 * code[2]
        bb = 0.0556434 * code[0] - 0.2040259 * code[1] + 1.0572252 * code[2]
        res[0] = xyz_to_rgb_helper(rn) * 255
        res[1] = xyz_to_rgb_helper(gb) * 255
        res[2] = xyz_to_rgb_helper(bb) * 255
        return res

    if model == 'lab':
        (x, y, z) = (
            lab_helper(code[1] / 500.0 + (code[0] + 16) / 116.0) * white[0],
            lab_helper((code[0] + 16) / 116.0) * white[1],
            lab_helper((code[0] + 16) / 116.0 - code[2] / 200.0) * white[2]
        )

        rn = 3.2406 * x / 100.0 - 1.5372 * y / 100.0 - 0.4986 * z / 100.0
        gn = -0.9689 * x / 100.0 + 1.8758 * y / 100.0 + 0.0415 * z / 100.0
        bn = 0.0557 * x / 100.0 - 0.2040 * y / 100.0 + 1.0570 * z / 100.0

        res[0] = round(min(255, max(0, round(xyz_to_rgb_helper(rn) * 255))))
        res[1] = round(min(255, max(0, round(xyz_to_rgb_helper(gn) * 255))))
        res[2] = round(min(255, max(0, round(xyz_to_rgb_helper(bn) * 255))))
        return res

    return res


def all_to_lab(code: list, model: str) -> list:
    res = [0, 0, 0]

    for i in range(len(code)):
        code[i] = float(code[i])

    if model == 'xyz':
        res[0] = (116 * lab_helper(code[1] / 100)) - 16
        res[1] = 500 * (lab_helper(code[0] / 95.047) - lab_helper(code[1] / 100))
        res[2] = 200 * (lab_helper(code[1] / 100) - lab_helper(code[2] / 108.883))
        return res

    if model == 'cmyk':
        rgbn = all_to_rgb(code, 'cmyk')
        xyzn = all_to_xyz(rgbn, 'rgb')
        res = all_to_lab(xyzn, 'xyz')
        return res

    if model == 'rgb':
        rn = one_more_xyz_to_rgb(code[0] / 255)
        gn = one_more_xyz_to_rgb(code[1] / 255)
        bn = one_more_xyz_to_rgb(code[2] / 255)

        x = 100 * (0.4125 * rn + 0.3576 * gn + 0.1804 * bn)
        y = 100 * (0.2127 * rn + 0.7152 * gn + 0.0722 * bn)
        z = 100 * (0.0193 * rn + 0.1192 * gn + 0.9502 * bn)

        res[0] = 116 * lab_helper(y / white[1]) - 16
        res[1] = 500 * (lab_helper(x / white[0]) - lab_helper(y / white[1]))
        res[2] = 200 * (lab_helper(y / white[1]) - lab_helper(z / white[2]))
        return res

    return res


def all_to_xyz(code: list, model: str) -> list:
    res = [0, 0, 0]
    for i in range(len(code)):
        code[i] = float(code[i])

    if model == 'rgb':
        r, g, b = code[0], code[1], code[2]
        rn = 100 * one_more_xyz_to_rgb(r / 255)
        gn = 100 * one_more_xyz_to_rgb(g / 255)
        bn = 100 * one_more_xyz_to_rgb(b / 255)
        res[0] = (rn * 0.4124) + (gn * 0.3576) + (bn * 0.1805)
        res[1] = (rn * 0.2126) + (gn * 0.7152) + (bn * 0.0722)
        res[2] = (rn * 0.0193) + (gn * 0.1192) + (bn * 0.9505)
        return res

    if model == 'lab':
        l, a, b = code[0], code[1], code[2]
        var_y = (l + 16) / 116
        var_x = (a / 500) + var_y
        var_z = var_y - (b / 200)

        if var_y ** 3 > 0.008856:
            var_y = var_y ** 3
        else:
            var_y = (var_y - 16 / 116) / 7.787
        if var_x ** 3 > 0.008856:
            var_x = var_x ** 3
        else:
            var_x = (var_x - 16 / 116) / 7.787
        if var_z ** 3 > 0.008856:
            var_z = var_z ** 3
        else:
            var_z = (var_z - 16 / 116) / 7.787

        res[0] = var_x * 95.047
        res[1] = var_y * 100.0
        res[2] = var_z * 108.883
        return res

    if model == 'cmyk':
        rgbn = all_to_rgb(code, 'cmyk')
        res = all_to_xyz(rgbn, 'rgb')
        return res

    pass


def all_to_cmyk(code: list, model: str) -> list:
    res = [0, 0, 0, 0]

    for i in range(len(code)):
        code[i] = float(code[i])

    if model == 'rgb':
        k = min(min(1 - code[0] / 255, 1 - code[1] / 255), 1 - code[2] / 255)
        if k == 1:
            return [0, 0, 0, 100]
        res[0] = round((1 - (code[0] / 255.0) - k) / (1 - k) * 100)
        res[1] = round((1 - (code[1] / 255.0) - k) / (1 - k) * 100)
        res[2] = round((1 - (code[2] / 255.0) - k) / (1 - k) * 100)
        res[3] = k * 100
        return res

    if model == 'lab':
        rgbn = all_to_rgb(code, 'lab')
        res = all_to_cmyk(rgbn, 'rgb')
        return res

    if model == 'xyz':
        rgbn = all_to_rgb(code, 'xyz')
        res = all_to_cmyk(rgbn, 'rgb')
        return res

    return res


cmyk = [100, 0, 0, 0]
lab = [91.116521109, -48.079618466, -14.138127755]
xyz = [53.8, 78.7, 107]
color = [0, 255, 255]


@app.route('/', methods=['GET', 'POST'])
def index():
    global cmyk
    global lab
    global xyz
    global color

    if request.method == 'POST':
        logging.debug('POST request spotted.')
        res = request.get_json()
        edited_element = res['editedElement']
        logging.debug(f'Edited element: { edited_element }')
        logging.debug(f'Values in request: {json.dumps(res)}')

        if 'color-picker' in edited_element:
            hex_color = res['inputData']
            color[0], color[1], color[2] = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))

            cmyk = all_to_cmyk(color.copy(), 'rgb')
            lab = all_to_lab(color.copy(), 'rgb')
            xyz = all_to_xyz(color.copy(), 'rgb')
            logging.debug(f'New RGB color: {str(color)}')

        if 'cmyk' in edited_element:
            if '1' in edited_element:
                cmyk = [res['formData']['cmyk_c1'], res['formData']['cmyk_m1'], res['formData']['cmyk_y1'],
                        res['formData']['cmyk_k1']]
            else:
                cmyk = [res['formData']['cmyk_c'], res['formData']['cmyk_m'], res['formData']['cmyk_y'],
                        res['formData']['cmyk_k']]

            logging.debug(f'New CMYK values: {str(cmyk)}')

            cmyk1 = []
            for i in range(len(cmyk)):
                cmyk1.append(int(cmyk[i]) / 100)

            color = all_to_rgb(cmyk1.copy(), 'cmyk')
            lab = all_to_lab(cmyk1.copy(), 'cmyk')
            xyz = all_to_xyz(cmyk1.copy(), 'cmyk')
            logging.debug(f'New RGB color: {str(color)}')

        if 'lab' in edited_element:
            if '1' in edited_element:
                lab = [res['formData']['lab_l1'], res['formData']['lab_a1'], res['formData']['lab_b1']]
            else:
                lab = [res['formData']['lab_l'], res['formData']['lab_a'], res['formData']['lab_b']]

            logging.debug(f'New LAB values: {str(lab)}')
            cmyk = all_to_cmyk(lab.copy(), 'lab')
            xyz = all_to_xyz(lab.copy(), 'lab')
            color = all_to_rgb(lab.copy(), 'lab')

        if 'xyz' in edited_element:
            if '1' in edited_element:
                xyz = [res['formData']['xyz_x1'], res['formData']['xyz_y1'], res['formData']['xyz_z1']]
            else:
                xyz = [res['formData']['xyz_x'], res['formData']['xyz_y'], res['formData']['xyz_z']]

            logging.debug(f'New XYZ values: {str(xyz)}')
            cmyk = all_to_cmyk(xyz.copy(), 'xyz')
            lab = all_to_lab(xyz.copy(), 'xyz')
            color = all_to_rgb(xyz.copy(), 'xyz')
            logging.debug(f'New RGB color: {str(color)}')

        return render_template('index.html', color="#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1])
                                                                                , int(color[2])), cmyk=cmyk,
                               lab=lab, xyz=xyz), 200

    if request.method == 'GET':
        return render_template('index.html', color="#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1])
                                                                                , int(color[2])), cmyk=cmyk,
                               lab=lab, xyz=xyz), 200


if __name__ == '__main__':
    app.run(debug=True)
