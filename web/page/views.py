
import json
import logging
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Ingredient
from .forms import IngredientForm
from taggit.models import Tag


# Create your views here.
###urls
def base(request):
    return render(request, 'base.html', {})

def rezepte(request):
    rezepte = ['Rezept 1', 'Rezept 2', 'Rezept 3']  # Dummy-Daten für Rezepte
    return render(request, 'pages/rezepte.html', {'rezepte': rezepte})


def ingredients_list(request):
    ingredients = Ingredient.objects.all()
    used_tags = Tag.objects.all()
    
    return render(request, 'pages/ingredients_list.html', {'ingredients': ingredients, 'used_tags': used_tags})

def add_ingredients(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
            return redirect('ingredients_list')
    else:
        form = IngredientForm()
        used_tags = Tag.objects.all()

    return render(request, 'pages/add_ingredients.html', {'form': form, 'used_tags': used_tags})

def update_quantity(request, ingredient_id):
    logger = logging.getLogger(__name__)
    logger.info(f"Change quantity")
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    if request.method == 'POST':

        data = json.loads(request.body)
        new_quantity = data.get('new_quantity')
        ingredient.quantity = new_quantity
       
        logger.info(f"Die Anzahl ist {new_quantity}")
        if new_quantity == 0:
            if ingredient.img:
                image_path = os.path.join(settings.MEDIA_ROOT, str(ingredient.img))
                if default_storage.exists(image_path):
                    default_storage.delete(image_path)
            
            ingredient.delete()
            logger.info(f"Die Zutat {ingredient_id} wurde erfolgreich gelöscht.")
     
            return JsonResponse({'success': True, 'message': 'Zutat erfolgreich gelöscht.'})
        ingredient.save()
        return JsonResponse({'success': True, 'new_quantity': new_quantity})
    logger.error("Fehler beim Aktualisieren der Anzahl.")
    return JsonResponse({'success': False})
