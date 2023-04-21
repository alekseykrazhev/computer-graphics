from flask import Flask, render_template, request, redirect, url_for
import numpy as np
from PIL import Image
import os
import cv2

app = Flask(__name__)


def init():
    image_list_clear = []
    image_list_dirty = []
    path = ['Images']
    for file_name in os.listdir(os.path.join(*path)):
        path.append(file_name)
        img = Image.open(os.path.join(*path))
        arr = np.array(img)
        img.close()
        if file_name[:5] == 'dirty':
            image_list_dirty.append(arr)
        else:
            image_list_clear.append(arr)

        path.pop()
    return image_list_clear, image_list_dirty


def f1(im):
    img_grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # зададим порог
    thresh = 100
    # получим картинку, обрезанную порогом
    ret, thresh_img = cv2.threshold(img_grey, thresh, 255, cv2.THRESH_BINARY)
    # надем контуры
    contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # создадим пустую картинку
    img_contours = np.zeros(im.shape)
    # отобразим контуры
    cv2.drawContours(img_contours, contours, -1, (255, 255, 255), 1)
    return img_contours.astype(np.uint8)


def local1_Otsu(img):  # img in grey
    min_ = img.min()
    max_ = img.max()

    histSize = max_ - min_ + 1
    hist = [0] * histSize

    for i in img:
        for val in i:
            hist[val - min_] += 1

    m = 0
    n = 0

    for t in range(max_ - min_ + 1):
        m += t * hist[t]
        n += hist[t]

    maxSigma = -1
    threshold = 0

    alpha1 = 0
    beta1 = 0

    for t in range(max_ - min_):
        alpha1 += t * hist[t]
        beta1 += hist[t]

    w1 = float(beta1) / n

    a = float(alpha1) / beta1 - float(m - alpha1) / (n - beta1)

    sigma = w1 * (1 - w1) * a * a

    if sigma > maxSigma:
        maxSigma = sigma
        threshold = t

    threshold += min_
    return threshold


def local1(img):  # in gray
    mean_img = Image.fromarray(img).convert('L')
    ret2, th2 = cv2.threshold(np.array(mean_img), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th2


def local2(img):  # in gray
    mean_img = Image.fromarray(img).convert('L')
    ret2, th2 = cv2.threshold(np.array(mean_img), 0, 255, cv2.THRESH_TRIANGLE)
    return th2


def adaptive1(img):
    mean_img = Image.fromarray(img).convert('L')
    arr2 = cv2.adaptiveThreshold(np.array(mean_img), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 20)
    return arr2.astype(np.uint8)


def adaptive2(img):
    mean_img = Image.fromarray(img).convert('L')
    arr2 = cv2.adaptiveThreshold(np.array(mean_img), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 20)
    return arr2.astype(np.uint8)


def save_images(indx):
    image_list_clear, image_list_dirty = init()

    path1 = 'static/trash/img.jpeg'
    path2 = 'static/trash/img1.jpeg'
    path3 = 'static/trash/img3.jpeg'
    path4 = 'static/trash/img4.jpeg'
    path5 = 'static/trash/img5.jpeg'
    path6 = 'static/trash/img6.jpeg'

    img1 = Image.fromarray(image_list_dirty[indx])
    img1.save(path1, 'JPEG')

    img2 = Image.fromarray(f1(image_list_dirty[indx]))
    img2.save(path2, 'JPEG')

    img3 = Image.fromarray(local1(image_list_dirty[indx]))
    img3.save(path3, 'JPEG')

    img4 = Image.fromarray(local2(image_list_dirty[indx]))
    img4.save(path4, 'JPEG')

    img5 = Image.fromarray(adaptive1(image_list_dirty[indx]), mode='L')
    img5.save(path5, 'JPEG')

    img6 = Image.fromarray(adaptive1(image_list_dirty[indx]), mode='L')
    img6.save(path6, 'JPEG')

    return [
        'trash/img.jpeg',
        'trash/img1.jpeg',
        'trash/img3.jpeg',
        'trash/img4.jpeg',
        'trash/img5.jpeg',
        'trash/img6.jpeg'
    ]


ind = 1


@app.route('/', methods=['GET', 'POST'])
def index():
    global ind
    images = save_images(ind)

    if request.method == 'POST':
        ind = int(request.json['inputField'])
        print(ind)
        images = save_images(ind)
        return render_template('index.html', images = images)

    return render_template('index.html', images=images)


if __name__ == '__main__':
    app.run()
