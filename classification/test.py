from tkinter import Tk
from tkinter.filedialog import askopenfilename
import tensorflow as tf
import os
from keras.models import load_model
import numpy as np


def open_file():
    Tk().withdraw()  # Versteckt das Hauptfenster des Tkinter-Fensters
    filename = askopenfilename()  # Öffnet den Dateiauswahldialog
    if filename:
        with open(filename, 'r') as file:
            
            return filename

## Main

batch_size = 32
img_height = 256
img_width = 256

current_path = os.path.dirname(os.path.realpath(__file__))


testfile = open_file()
print(testfile)

img = tf.keras.utils.load_img(
    testfile, target_size=(img_height, img_width)
)

img_array = tf.keras.utils.img_to_array(img)
img_array = tf.expand_dims(img_array, 0) # Create a batch

model = load_model(current_path + '\\classification_network.h5')

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])


class_names = ['Banane', 'Frischmilch', 'MilchLaktosefrei']

print(
    "This image most likely belongs to {} with a {:.2f} percent confidence."
    .format(class_names[np.argmax(score)], 100 * np.max(score))
)