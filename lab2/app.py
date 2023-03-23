import logging
import os

from PIL import Image
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
logging.basicConfig(filename='backend.log', level=logging.DEBUG)
folder = '/home/alex/Downloads/ДляпроверкиLab2'


def get_image_info(filepath):
    with Image.open(filepath) as img:
        filename = str(os.path.basename(filepath))
        logging.debug(f'FILENAME | {filename} loaded.')
        size = img.size
        dpi = img.info.get('dpi')
        if dpi is None:
            dpi = (72, 72)
        dpi = min(size[0] * size[1] // ((13 * 2.54) ** 2), 90)
        mode = img.mode
        compression = img.info.get('compression')

        depth = img.info.get('bits', 8)
        channels = len(img.getbands())
        bit_depth = depth * channels

        original_size = os.path.getsize(filepath)
        original_pixels = size[0] * size[1]
        original_bits_per_pixel = original_size / original_pixels

        return {
            'filename': filename,
            'size': size,
            'dpi': dpi,
            'mode': mode,
            'depth': bit_depth,
            'compression': compression,
            'degree': original_bits_per_pixel
        }


def get_images_info(folder):
    images_info = []
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            try:
                image_info = get_image_info(filepath)
                images_info.append(image_info)
            except Exception as e:
                logging.debug(f"ERROR | Error getting info for file {filename}: {e}")
    return images_info


@app.route('/')
def index():
    info_res = get_images_info(folder)
    return render_template('index.html', info_list=info_res), 200


@app.route('/default')
def default():
    global folder
    folder = '/home/alex/Downloads/ДляпроверкиLab2'
    return redirect(url_for('index')), 308


@app.route('/peliculas')
def peliculas():
    global folder
    folder = '/home/alex/Downloads/peliculas-animadas'
    return redirect(url_for('index')), 308


@app.route('/png')
def png():
    global folder
    folder = '/home/alex/Downloads/png'
    return redirect(url_for('index')), 308


if __name__ == '__main__':
    app.run()
