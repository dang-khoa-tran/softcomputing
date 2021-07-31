import load_data
from tensorflow.python.ops.gen_math_ops import maximum
from tensorflow.python.util.nest import flatten
from tensorflow.python.ops.gen_array_ops import shape
from tensorflow.python.keras.engine import input_layer
from tensorflow.python.ops.gradients_util import _Inputs
import tensorflow as tf


# import tensorflow_hub as hub
import time
import string

import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from PIL import Image
from os import listdir

plt.rcParams["figure.figsize"] = (13.0, 8.0)
Wordlength = 16

chars = " 0123456789" + string.ascii_uppercase + string.ascii_lowercase
print(chars)


def read_img(path):
    img = Image.open(path).convert("L")

    # img = img.resize((32, 32))
    return np.asarray(img) / 255


def load_data():
    imgFolder = list(
        filter(
            lambda x: not x.startswith("."), listdir("./mnt/ramdisk/max/90kDICT32px")
        )
    )
    imgFolder.sort()

    images = {}
    for path in imgFolder[0:1]:
        path = "1"
        imgPaths = listdir("mnt/ramdisk/max/90kDICT32px/{}".format(path))
        imgPaths.sort()
        for i in imgPaths:
            imageFolder = listdir("mnt/ramdisk/max/90kDICT32px/{}/{}".format(path, i))
            imageFolder.sort()
            for image in imageFolder:
                # print(image)
                label = image.split("_")[1]
                label = label + "".join([" " for _ in range(32 - len(label))])
                # print(label, ".")
                currentImage = read_img(
                    "mnt/ramdisk/max/90kDICT32px/{}/{}/{}".format(path, i, image)
                )
                # print(np.shape(currentImage))
                currentImage = np.pad(
                    currentImage,
                    ((0, 32 - len(currentImage)), (0, 512 - len(currentImage[0]))),
                    mode="constant",
                )
                # print(np.shape(currentImage))
                if not (label in images):
                    images[label] = []
                # else:
                #     print(images.keys())
                # print(type(images[label]))
                images[label].append(currentImage)

    return images


""" def load_data():
    imgFolder = list(filter(lambda x: not x.startswith("."), listdir("Images")))
    imgFolder.sort()

    images = {}
    i = 0
    for path in imgFolder:
        imgPaths = listdir("Images/{}".format(path))
        imgPaths.sort()
        images[chars[i]] = [read_img("Images/{}/{}".format(path, x)) for x in imgPaths]
        i = i + 1

    return images
 """


def split_data(labels, imgs):
    border = round(len(labels) * 0.8)
    training = (labels[:border], imgs[:border])
    test = (labels[border:], imgs[border:])
    return training, test


def flatten_dictionary(data):
    labels = []
    imgs = []
    max = 0
    for (key, imgArray) in data.items():
        idx = np.array([chars.find(c) for c in key])
        for img in imgArray:
            labels.append(idx)
            max = maximum(max, len(img))
            imgs.append(img)
    print("Here:", np.shape(imgs))
    return np.array(labels, dtype="int"), np.array(imgs)


def split_labels(labels):
    results = [[] for _ in range(Wordlength)]

    for label in labels:
        for i in range(Wordlength):
            results[i].append(label[i])

    return {f"output_{i}": np.asarray(results[i]) for i in range(Wordlength)}


def train(data):
    labels, imgs = split_labels(data[0]), data[1]
    
    model = tf.keras.models.load_model('model_trained1')

    print(model.summary())
    # print(imgs.shape, labels.shape)
    model.fit(imgs.reshape(len(imgs), 32, 512, 1), labels, batch_size=32, epochs=5)
    return model


def evaluate(data, model):
    labels, imgs = split_labels(data[0]), data[1]

    print(model.evaluate(imgs.reshape(len(imgs), 32, 512, 1), labels, verbose=2)[Wordlength:])

def load(file):
    with open('test.npy', 'rb') as f:
        data = np.load(f)
        labels = data['labels']
        imgs = data['imgs']
    return labels, imgs



config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.compat.v1.Session(config=config)

#data = load_data()
# labels, imgs = flatten_dictionary(data)
#print(imgs.shape, labels.shape)
labels, imgs = load('collected_data.npy')

config.gpu_options.per_process_gpu_memory_fraction = 0.4
training, test = split_data(labels, imgs)

# for line in training["A"][0]:
#     print(line)

# plt.imshow(training["A"][0])
# plt.show()

model = train(training)

evaluate(test, model)

model.save("model_trained1")

print("HIER")
