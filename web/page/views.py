
import json
import logging
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Zutat
from .forms import ZutatForm

# Create your views here.
###urls
def base(request):
    return render(request, 'base.html', {})

def rezepte(request):
    rezepte = ['Rezept 1', 'Rezept 2', 'Rezept 3']  # Dummy-Daten für Rezepte
    return render(request, 'pages/rezepte.html', {'rezepte': rezepte})



###helpers
def zutaten_liste(request):
    zutaten = Zutat.objects.all()
    return render(request, 'pages/zutaten_liste.html', {'zutaten': zutaten})

def zutat_hinzufuegen(request):
    if request.method == 'POST':
        form = ZutatForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('zutaten_liste')
    else:
        form = ZutatForm()
    return render(request, 'pages/add_zutat.html', {'form': form})

def update_quantity(request, zutat_id):
    logger = logging.getLogger(__name__)
    logger.info(f"Anzahl ändern")
    zutat = get_object_or_404(Zutat, id=zutat_id)
    if request.method == 'POST':

        data = json.loads(request.body)
        new_quantity = data.get('new_quantity')
        zutat.anzahl = new_quantity
       
        logger.info(f"Die Anzahl ist {new_quantity}")
        if new_quantity == 0:
            if zutat.bild:
                image_path = os.path.join(settings.MEDIA_ROOT, str(zutat.bild))
                if default_storage.exists(image_path):
                    default_storage.delete(image_path)
            
            zutat.delete()
            logger.info(f"Die Zutat {zutat_id} wurde erfolgreich gelöscht.")
     
            return JsonResponse({'success': True, 'message': 'Zutat erfolgreich gelöscht.'})
        zutat.save()
        return JsonResponse({'success': True, 'new_quantity': new_quantity})
    logger.error("Fehler beim Aktualisieren der Anzahl.")
    return JsonResponse({'success': False})


