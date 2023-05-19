import os
from uuid import uuid4
from django.db import models

    
### Helpers

def upload_image(instance, filename):
    # Erzeuge einen eindeutigen Dateinamen
    unique_filename = str(uuid4())

    # Hole die Dateierweiterung der hochgeladenen Datei
    extension = os.path.splitext(filename)[1]

    # Füge den eindeutigen Dateinamen und die Erweiterung zusammen
    new_filename = unique_filename + extension

    # Gib den Pfad zurück, unter dem die Datei gespeichert werden soll
    return os.path.join('zutaten/', new_filename)



### Models
# Create your models here.
class Zutat(models.Model):
    bild = models.ImageField(upload_to=upload_image)
    beschreibung = models.TextField()
    mindesthaltbarkeitsdatum = models.DateField()
    anzahl = models.PositiveIntegerField()
    rubrik = models.CharField(max_length=255)
    
    
    
