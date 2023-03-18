from flask import Flask, render_template
from PIL import Image
import os

app = Flask(__name__)


def get_image_info(filepath):
    with Image.open(filepath) as img:
        filename = os.path.basename(filepath)
        size = img.size
        dpi = img.info.get('dpi')
        mode = img.mode
        compression = img.info.get('compression')

        return {
            'filename': filename,
            'size': size,
            'dpi': dpi,
            'mode': mode,
            'compression': compression
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
                print(f"Error getting info for file {filename}: {e}")
    return images_info


@app.route('/')
def hello_world():
    folder = '/home/alex/Downloads/ДляпроверкиLab2'
    info_res = get_images_info(folder)
    return render_template('index.html', info_list=info_res), 200


if __name__ == '__main__':
    app.run()
