from django.shortcuts import render, redirect
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