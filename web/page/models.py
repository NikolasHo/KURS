from django.db import models

# Create your models here.
class Zutat(models.Model):
    bild = models.ImageField(upload_to='zutaten/')
    beschreibung = models.TextField()
    mindesthaltbarkeitsdatum = models.DateField()
    anzahl = models.PositiveIntegerField()
    rubrik = models.CharField(max_length=255)