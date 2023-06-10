from django.urls import path
from . import views

urlpatterns = [
    path('ingredients/', views.ingredients_list, name='ingredients_list'),
    path('ingredients/add/', views.add_ingredients, name='add_ingredients'),
   # path('ingredients/add_multi/', views.add_multi_ingredients, name='add_multi_ingredients'),
    path('update_quantity/<int:ingredient_id>/', views.update_quantity, name='update_quantity'),
    path('image_classification/', views.image_classification, name='image_classification'),
    path('classification', views.classification_base, name='classification'),
    path('recipe/add', views.add_recipe, name='add_recipe'),
    path('recipe', views.recipe_list, name='recipe_list'),
    path('getIngredients/', views.get_ingredients, name='get_ingredients'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('', views.base, name='base'),
]