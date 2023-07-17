import numpy as np
from PIL import Image
import os
import tensorflow as tf
import matplotlib.pyplot as plt
import pathlib
import json
import classification.classification_settings as classification_settings

from tensorflow import keras
from keras import layers
from keras.models import Sequential
from keras.models import save_model



####Main



  
def train_classification_network():
  
  # Defines for network
  batch_size = 32
  img_height = 256
  img_width = 256



  # How many images are available:
  training_dir = pathlib.Path(classification_settings.CLASSIFICATION_FILES)
  image_count = len(list(training_dir.glob('*/*.jpeg')))
  print(image_count)

  # Prepare training files
  train_ds = tf.keras.utils.image_dataset_from_directory(
    training_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size)

  val_ds = tf.keras.utils.image_dataset_from_directory(
    training_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size)

  class_names = train_ds.class_names
  print(class_names)
  with open(classification_settings.CLASSIFICATION_CLASSES_FULLNAME, 'w') as f:
      json.dump(class_names, f)


  if not os.path.exists(classification_settings.CLASSIFICATION_TRAINED_FILES_TMP):
      os.makedirs(classification_settings.CLASSIFICATION_TRAINED_FILES_TMP)

  # Speichern jedes Bildes aus dem train_ds-Datensatz
  for i, (images, labels) in enumerate(train_ds.take(1)):
      for j in range(len(images)):
          image = images[j].numpy().astype("uint8")
          label = class_names[labels[j]]

          # Pfad zum Speichern des Bildes erstellen
          filename = f"{label}_{i * len(images) + j}.jpg"
          filepath = os.path.join(classification_settings.CLASSIFICATION_TRAINED_FILES_TMP, filename)

          # Bild speichern
          plt.imsave(filepath, image)

          print(f"Gespeichertes Bild: {filepath}")
    
      
      

  for image_batch, labels_batch in train_ds:
    print(image_batch.shape)
    print(labels_batch.shape)
    break

  # Prepare for better performance
  AUTOTUNE = tf.data.AUTOTUNE

  train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
  val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

  # Standardize
  normalization_layer = layers.Rescaling(1./255)

  normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
  image_batch, labels_batch = next(iter(normalized_ds))
  first_image = image_batch[0]
  # Notice the pixel values are now in `[0,1]`.
  print(np.min(first_image), np.max(first_image))

  # CNN-Modell erstellen
  num_classes = len(class_names)

  model = Sequential([
    layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
    layers.Conv2D(16, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(num_classes)
  ])

  try:  
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    model.summary()

    epochs=10
    history = model.fit(
      train_ds,
      validation_data=val_ds,
      epochs=epochs
    )

    save_model(model, classification_settings.CLASSIFICATION_MODEL_FULLNAME)
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(epochs)


    # Visual training
   # plt.figure(figsize=(8, 8))
    #plt.subplot(1, 2, 1)
   # plt.plot(epochs_range, acc, label='Training Accuracy')
    #plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    #plt.legend(loc='lower right')
    #plt.title('Training and Validation Accuracy')

    #plt.subplot(1, 2, 2)
    #plt.plot(epochs_range, loss, label='Training Loss')
    #plt.plot(epochs_range, val_loss, label='Validation Loss')
    #plt.legend(loc='upper right')
    #plt.title('Training and Validation Loss')
    #plt.show()
    return "Success"
  except Exception as e:
    return "Error"