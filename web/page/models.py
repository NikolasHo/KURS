import os
from uuid import uuid4
from django.db import models
from taggit.managers import TaggableManager

    
### Helpers
def upload_image(instance, filename):
    # Erzeuge einen eindeutigen Dateinamen
    unique_filename = str(uuid4())

    # Hole die Dateierweiterung der hochgeladenen Datei
    extension = os.path.splitext(filename)[1]

    # Füge den eindeutigen Dateinamen und die Erweiterung zusammen
    new_filename = unique_filename + extension

    # Gib den Pfad zurück, unter dem die Datei gespeichert werden soll
    return os.path.join('ingredients/', new_filename)



### Models

class Ingredient(models.Model):
    img = models.ImageField(upload_to=upload_image)
    description = models.TextField()
    mhd = models.DateField()
    quantity = models.PositiveIntegerField()
    tags = TaggableManager()
    weight = models.PositiveIntegerField()
    
    
    
