from django.contrib import admin

# Register your models here.
from .models import Ingredient, recipe, recipe_step

admin.site.register(Ingredient)
admin.site.register(recipe)
admin.site.register(recipe_step)