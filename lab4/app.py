from flask import Flask, render_template, request, redirect, url_for
from controller import handle_method

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    x1, x2, y1, y2, x, y, r = 0, 0, 0, 0, 0, 0, 0

    if request.method == 'GET':
        return render_template('index.html'), 200

    if request.method == 'POST':
        method = request.form['method']
        if method == 'okr':
            x, y, r = request.form['x'], request.form['y'], request.form['r']
        else:
            x1 = request.form['x1']
            x2 = request.form['x2']
            y1 = request.form['y1']
            y2 = request.form['y2']
        # print(method)

        res = handle_method(x1, x2, y1, y2, x, y, r, method)

        if res == 'Not int':
            return 'Not an integer!'

        return redirect(url_for('index'))

    return render_template('index.html'), 200


if __name__ == '__main__':
    app.run()
