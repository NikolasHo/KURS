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
    return os.path.join('images/', new_filename)



### Models

class Ingredient(models.Model):
    img = models.ImageField(upload_to=upload_image,null=True, blank=True)
    description = models.TextField(default="")
    mhd = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)
    part_of_recipe = models.BooleanField()
    pass
    
    
class recipe_step(models.Model):
    recipe_step_img = models.ImageField(upload_to=upload_image, blank=True, null=True)
    recipe_step_headline = models.TextField(default="")
    recipe_step_description = models.TextField(default="")
    recipe_step_ingredients = models.ManyToManyField(Ingredient)
    pass
    
class recipe(models.Model):
    img = models.ImageField(upload_to=upload_image)
    headline = models.TextField(default="")
    description = models.TextField(default="")
    recipe_steps = models.ManyToManyField(recipe_step)
    ingredients = models.ManyToManyField(Ingredient)

# Bills
class bills(models.Model):
    bill_img = models.ImageField(upload_to=upload_image, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)