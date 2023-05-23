from django.contrib import admin

# Register your models here.
from .models import Ingredient

admin.site.register(Ingredient)