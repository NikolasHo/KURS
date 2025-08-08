from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    
    #Ingredients
    path('ingredients/', views.ingredients_list, name='ingredients_list'),
    path('ingredients_lists/', views.ingredients_list_lists, name='ingredients_list_lists'),
    path('ingredients/add/', views.add_ingredients, name='add_ingredients'),
    path('ingredients/delete/', views.delete_ingredient, name='delete_ingredient'),
    path('getIngredients/', views.get_ingredients, name='get_ingredients'),
    path('ingredients/add_detected_editable/', views.detect_ingredients_editable, name='add_ingredients_editable'),
    path('ingredients/save_detected/', views.save_edited_ingredients, name='save_detected_ingredients'),

   # path('ingredients/add_multi/', views.add_multi_ingredients, name='add_multi_ingredients'),
    path('update_quantity/<int:ingredient_id>/', views.update_quantity, name='update_quantity'),
    
    #Recpides
    path('recipe/add', views.add_recipe, name='add_recipe'),
    path('recipe', views.recipe_list, name='recipe_list'),
    path('recipe/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/cooked/<int:recipe_id>/', views.cooked_recipe, name='cooked_recipe'),
    path('suggestedrecipes/', views.suggested_recipes, name='suggested_recipes'),
    path('suggestedrecipeskeyword/', views.suggested_recipes_keyword, name='suggested_recipes_keyword'),
    
    
    #MAIN
    path('', views.base, name='base'),
    
    #KI
    path('upload_training/', views.upload_training_image, name='upload_training_image'),
    path('add-class/', views.add_class_name, name='add_class_name'),
    path('annotate-image/', views.annotate_image, name='annotate_image'),
    path('upload-annotated-image-existing/', views.upload_annotated_image_existing, name='upload_annotated_image_existing'),
    path('train-model/', views.train_model, name='train_model'),
    path('bulk-add/', views.bulk_add_ingredients, name='bulk_add_ingredients'),
    path('detect-list/', views.detect_and_list, name='detect_and_list'),
    path('bulk-save/', views.bulk_save_ingredients, name='bulk_save_ingredients'),
    path('test-detect/', views.test_detection, name='test_detection'),

    #Dev
    path('test/', views.test, name='test'),
    
    
    #Settings
    path('settings/', views.settings_site, name='settings_site'),
    path('backup/', views.backup_database, name='backup_database'),
    path('backup_restore/', views.restore_database, name='restore_database'),
    path('backup_delete/', views.delete_backup, name='delete_backup'),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)