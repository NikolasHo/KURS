from django.urls import path
from . import views

urlpatterns = [
    path('ingredients/', views.ingredients_list, name='ingredients_list'),
    path('ingredients/add/', views.add_ingredients, name='add_ingredients'),
    path('getIngredients/', views.get_ingredients, name='get_ingredients'),
   # path('ingredients/add_multi/', views.add_multi_ingredients, name='add_multi_ingredients'),
    path('update_quantity/<int:ingredient_id>/', views.update_quantity, name='update_quantity'),
    path('recipe/add', views.add_recipe, name='add_recipe'),
    path('recipe', views.recipe_list, name='recipe_list'),
    path('recipe/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/cooked/<int:recipe_id>/', views.cooked_recipe, name='cooked_recipe'),
    path('suggestedrecipes/', views.suggested_recipes, name='suggested_recipes'),
    path('suggestedrecipeskeyword/', views.suggested_recipes_keyword, name='suggested_recipes_keyword'),
    path('', views.base, name='base'),
    path('folders/', views.folder_list, name='folder_list'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/delete/', views.delete_folder, name='delete_folder'),
    path('images/upload/', views.upload_image, name='upload_image'),
    path('train_network/', views.train_network, name='train_network'),
    path('image_classification/', views.image_classification, name='image_classification'),
    path('classification', views.classification_base, name='classification'),
   
]