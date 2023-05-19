from django.urls import path
from . import views

urlpatterns = [
    path('rezepte/', views.rezepte, name='rezepte'),
    path('ingredients/', views.ingredients_list, name='ingredients_list'),
    path('ingredients/add/', views.add_ingredients, name='add_ingredients'),
    path('update_quantity/<int:ingredient_id>/', views.update_quantity, name='update_quantity'),
    path('', views.base, name='base'),
]