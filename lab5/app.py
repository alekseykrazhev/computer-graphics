from os import path

from matplotlib.pyplot import savefig, subplots
from matplotlib.patches import Rectangle
from io import BytesIO
from base64 import b64encode

from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
from algorithms import open_file, open_file1, liang_barsky, sutherland_hodgman


UPLOAD_FOLDER = path.abspath('static/files')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'ALPDKCFVNSUVSDCJSDIOJCD6'


def plot_lines_and_window(lines, window, clipped_lines):
    fig, ax = subplots()

    for line in lines:
        ax.plot([line[0], line[2]], [line[1], line[3]], 'r-')

    ax.add_patch(Rectangle((window[1], window[0]), window[3]-window[1], window[2]-window[0],
                           fill=False, edgecolor='blue'))

    for line in clipped_lines:
        ax.plot([line[0], line[2]], [line[1], line[3]], 'g-')

    buf = BytesIO()
    savefig(buf, format='png')
    buf.seek(0)
    return b64encode(buf.read()).decode('utf-8')


def handle_file(file):
    filename = secure_filename(file.filename)
    file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
    try:
        polygon, ends = open_file(filename)
        res = []
        for line in polygon:
            lg = liang_barsky(line[0], line[1], line[2], line[3], ends[0], ends[1], ends[2], ends[3])
            if lg:
                res.append(lg)
        image = plot_lines_and_window(polygon, ends, res)
    except FileNotFoundError:
        return 'Error opening file.'
    return image


def plot1(polygon, window, clipped):
    fig, ax = subplots()

    for line in polygon:
        res = []
        res1 = []
        for n in line:
            res.append(n[0])
            res1.append(n[1])
        res.append(line[0][0])
        res1.append(line[0][1])
        ax.plot(res, res1, 'r-')

    r = []
    r1 = []
    for n in window:
        r.append(n[0])
        r1.append(n[1])
    r.append(window[0][0])
    r1.append(window[0][1])
    ax.plot(r, r1, 'b-')

    for line in clipped:
        re = []
        re1 = []
        for n in line:
            re.append(n[0])
            re1.append(n[1])
        re.append(line[0][0])
        re1.append(line[0][1])
        ax.plot(re, re1, 'g-')

    buf = BytesIO()
    savefig(buf, format='png')
    buf.seek(0)
    return b64encode(buf.read()).decode('utf-8')


def handle_file1(file):
    filename = secure_filename(file.filename)
    file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
    try:
        polygon, ends = open_file1(filename)
        print(polygon, ends)
        res = []
        for line in polygon:
            sh = sutherland_hodgman(line, ends)
            if sh:
                res.append(sh)
        image = plot1(polygon, ends, res)
    except FileNotFoundError:
        return 'Error opening file.'
    return image


@app.route('/', methods=['GET', 'POST'])
def index():
    image = None
    image1 = None
    if request.method == 'GET':
        return render_template('index.html', image=False)

    if request.method == 'POST':
        if 'file' not in request.files or 'file1' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        file1 = request.files['file1']
        if file:
            image = handle_file(file)
        if file1:
            image1 = handle_file1(file1)

    return render_template('index.html', image=image, image1=image1)


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = True
    app.run(debug=True)
