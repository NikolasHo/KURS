## Defines for neuronal network
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CLASSIFICATION_MODEL_ROOT = os.path.join(BASE_DIR, 'classification')

CLASSIFICATION_MODEL = "classification_network.h5"

CLASSIFICATION_MODEL_FULLNAME = CLASSIFICATION_MODEL_ROOT + '\\' + CLASSIFICATION_MODEL

CLASSIFICATION_CLASSES = "classes.json"

CLASSIFICATION_CLASSES_FULLNAME = CLASSIFICATION_MODEL_ROOT + '\\' + CLASSIFICATION_CLASSES

CLASSIFICATION_FILES = CLASSIFICATION_MODEL_ROOT + '\\' + "trainsets"