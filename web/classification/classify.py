from tkinter import Tk
from tkinter.filedialog import askopenfilename
from keras.models import load_model

import tensorflow as tf
import os
import numpy as np
import json
import classification_settings
import matplotlib.pyplot as plt

## Main

batch_size = 32

def open_file():
    Tk().withdraw()  # Versteckt das Hauptfenster des Tkinter-Fensters
    filename = askopenfilename()  # Öffnet den Dateiauswahldialog
    if filename:
        with open(filename, 'r') as file:
            
            return filename

def classify_image(image):
    img_height = 256
    img_width = 256

    
    img = tf.keras.utils.load_img(
        image, target_size=(img_height, img_width)
    )

    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch

    # load trained model
    model = load_model(classification_settings.CLASSIFICATION_MODEL_FULLNAME)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    # load classes from file
    with open(classification_settings.CLASSIFICATION_CLASSES_FULLNAME, 'r') as f:
        loaded_class_names = json.load(f)
        
    target_class = loaded_class_names[np.argmax(score)]
    
        
    print(
        "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(loaded_class_names[np.argmax(score)], 100 * np.max(score))
    )
    
    return target_class    

def preprocess_image(image_path, target_size):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_objects(image_array, model, class_names):
    predictions = model.predict(image_array)
    scores = tf.nn.softmax(predictions[0])

    results = []
    for i in range(len(class_names)):
        class_name = class_names[i]
        confidence = 100 * scores[i]
        result = {
            'class_name': class_name,
            'confidence': confidence
        }
        results.append(result)
    
    return results

def classify_image_4(image):
    
    img_height_var = 512
    img_width_var = 512
    
        # load trained model
    model = load_model(classification_settings.CLASSIFICATION_MODEL_FULLNAME)

    # load classes from file
    with open(classification_settings.CLASSIFICATION_CLASSES_FULLNAME, 'r') as f:
        loaded_class_names = json.load(f)

    # Das Bild in 4 Teile aufteilen
    image = preprocess_image(testfile, target_size=(img_height_var, img_width_var))
    part_height = img_height_var // 2
    part_width = img_width_var // 2

    parts = []
    for i in range(2):
        for j in range(2):
            part = image[:, i * part_height:(i + 1) * part_height, j * part_width:(j + 1) * part_width, :]
            parts.append(part)



    # Objekterkennung für jedes Teil durchführen
    results = []
    for idx, part in enumerate(parts):
        part_results = predict_objects(part, model, loaded_class_names)
        results.extend(part_results)


    # Ergebnisse filtern
    filtered_results = [result for result in results if result['class_name'] in loaded_class_names]



    for idx, part in enumerate(parts):
        # Teilbild plotten
        plt.subplot(2, 2, idx+1)
        plt.imshow(part[0].astype(int))
        plt.axis('off')
        
    final_results = []    
    # Ergebnisse ausgeben
    if len(filtered_results) > 0:
        for result in filtered_results:
            if result['confidence'] > 60:
                
                final_results.append(result)
                print("Objekt: {}, Vertrauen: {:.2f}%".format(result['class_name'], result['confidence']))
    else:
        print("Nix gefunden")

    return final_results  

def classify_image_8(image):
    
    img_height_var = 1024
    img_width_var = 1024
    
        # load trained model
    model = load_model(classification_settings.CLASSIFICATION_MODEL_FULLNAME)

    # load classes from file
    with open(classification_settings.CLASSIFICATION_CLASSES_FULLNAME, 'r') as f:
        loaded_class_names = json.load(f)

    # Das Bild in 4 Teile aufteilen
    image = preprocess_image(testfile, target_size=(img_height_var, img_width_var))
    part_height = img_height_var // 4
    part_width = img_width_var // 4

    parts = []
    for i in range(4):
        for j in range(4):
            part = image[:, i * part_height:(i + 1) * part_height, j * part_width:(j + 1) * part_width, :]
            parts.append(part)



    # Objekterkennung für jedes Teil durchführen
    results = []
    for part in enumerate(parts):
        part_results = predict_objects(part, model, loaded_class_names)
        results.extend(part_results)


    # Ergebnisse filtern
    filtered_results = [result for result in results if result['class_name'] in loaded_class_names]

        
    # Ergebnisse ausgeben
    if len(filtered_results) > 0:
        for result in filtered_results:
            print("Objekt: {}, Vertrauen: {:.2f}%".format(result['class_name'], result['confidence']))
    else:
        print("Nix gefunden")

    return filtered_results  


#### Main

#testfile = open_file()
#print(testfile)

#classify_image(testfile)