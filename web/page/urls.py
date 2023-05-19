from django.urls import path
from . import views

urlpatterns = [
    path('rezepte/', views.rezepte, name='rezepte'),
    path('zutaten/', views.zutaten_liste, name='zutaten_liste'),
    path('zutaten/hinzufuegen/', views.zutat_hinzufuegen, name='zutat_hinzufuegen'),
    path('update_quantity/<int:zutat_id>/', views.update_quantity, name='update_quantity'),
    path('', views.base, name='base'),
]