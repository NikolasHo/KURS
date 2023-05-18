from django.urls import path
from . import views

urlpatterns = [
    path('rezepte/', views.rezepte, name='rezepte'),
    #path('zutaten/', views.zutaten, name='zutaten'),
    path('zutaten/', views.zutaten_liste, name='zutaten_liste'),
    path('zutaten/hinzufuegen/', views.zutat_hinzufuegen, name='zutat_hinzufuegen'),
    path('', views.base, name='base'),
]