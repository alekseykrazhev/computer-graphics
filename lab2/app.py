import logging
import os

from PIL import Image, JpegImagePlugin
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
logging.basicConfig(filename='backend.log', level=logging.DEBUG)
folder = os.path.abspath('pictures/ДляпроверкиLab2')


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
    logging.debug(f'PATH | {folder}')
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
    folder_size = round(sum(d.stat().st_size for d in os.scandir(folder) if d.is_file()) / 1024 ** 2, 2)
    return render_template('index.html', info_list=info_res, size=folder_size), 200


@app.route('/default')
def default():
    global folder
    folder = os.path.abspath('pictures/ДляпроверкиLab2')
    logging.debug(f'PATH | {folder}')
    return redirect(url_for('index'))


@app.route('/peliculas')
def peliculas():
    global folder
    folder = os.path.abspath('pictures/peliculas-animadas')
    logging.debug(f'PATH | {folder}')
    return redirect(url_for('index'))


@app.route('/png')
def png():
    global folder
    folder = os.path.abspath('pictures/png')
    logging.debug(f'PATH | {folder}')
    return redirect(url_for('index'))


@app.route('/custom', methods=['GET', 'POST'])
def custom():
    if request.method == 'GET':
        return render_template('custom_folder.html')
    if request.method == 'POST':
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
