
import json
import logging
import os
import classification.classification_settings as classification_settings
import classification.classify as classify
import classification.classification as classification
import io
import food.fwl as fwl
import shutil
import page.utils as utils 

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse 
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Ingredient, recipe
from .forms import IngredientForm
from taggit.models import Tag
from .forms import RecipeForm
from django.db import transaction
from datetime import datetime



logger = logging.getLogger(__name__)

# Create your views here.
###urls
def base(request):
    return render(request, 'base.html', {})

def test(request):
    return render(request, 'pages/test.html', {})


def ingredients_list(request):
    ingredients = Ingredient.objects.all()
    used_tags = Tag.objects.all()
    
    return render(request, 'pages/ingredients_list.html', {'ingredients': ingredients, 'used_tags': used_tags})


def ingredients_list_lists(request):
    ingredients = Ingredient.objects.filter(part_of_recipe=False)
    used_tags = Tag.objects.all()
    context = {'ingredients': ingredients, 'used_tags': used_tags}
    return render(request, 'pages/ingredients_list_lists.html', context)

# Form to add a new ingredient
def add_ingredients(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            
            try:
                print("Check: ", instance.description)
                
                available_ingredients = Ingredient.objects.filter(part_of_recipe=False)

                found_ingredient = available_ingredients.get(description=instance.description)
                # if it already exist, dont create a new entry
                print("Ingredient already exist:")
                print("Name:", found_ingredient.description)
                print("Quantity:", found_ingredient.quantity)
            except Ingredient.DoesNotExist:
                # Das Ingredient wurde nicht gefunden
                print("New Ingredient: ", instance.description)
                instance = form.save(commit=False)
                instance.part_of_recipe = False
                instance.save()
                form.save_m2m()
            
            return redirect('ingredients_list')
    else:
        form = IngredientForm()
        used_tags = Tag.objects.all()

    return render(request, 'pages/add_ingredients.html', {'form': form, 'used_tags': used_tags})

# Update quantity of ingredients (increase and decrease)
def update_quantity(request, ingredient_id):
    logger.info(f"Change quantity")
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    if request.method == 'POST':

        data = json.loads(request.body)
        new_quantity = data.get('new_quantity')
        ingredient.quantity = new_quantity
       
        logger.info(f"Die Anzahl ist {new_quantity}")
        # dont remove the entry, just set it to zero.
        
       # if new_quantity == 0:
            #if ingredient.img:
               # image_path = os.path.join(settings.MEDIA_ROOT, str(ingredient.img))
               
               # if default_storage.exists(image_path):
               #      default_storage.delete(image_path)
            
            #ingredient.delete()
            #logger.info(f"Die Zutat {ingredient_id} wurde erfolgreich gelöscht.")
        

        ingredient.save()
        return JsonResponse({'success': True, 'new_quantity': new_quantity})
    logger.error("Fehler beim Aktualisieren der Anzahl.")
    return JsonResponse({'success': False})


# Entry point for classification
    # all stuff with the neuronal network and its traingings files
def classification_base(request):

    # Überprüfen, ob der Ordner vorhanden ist
    if os.path.exists(classification_settings.CLASSIFICATION_CLASSES_FULLNAME):
       
        with open(classification_settings.CLASSIFICATION_CLASSES_FULLNAME, 'r') as f:
            AvailableClassNames = json.load(f)
        
        return render(request, 'pages/classification.html', {'AvailableClassNames': AvailableClassNames})
  
    return render(request, 'pages/classification.html')
  
  
def train_network(request):
    if request.method == 'POST':
        with open(classification_settings.CLASSIFICATION_CLASSES_FULLNAME, 'r') as f:
            AvailableClassNames = json.load(f)
        result = classification.train_classification_network()
    
        return render(request, 'pages/classification.html', {'AvailableClassNames': AvailableClassNames,'success': result})


# Classification of a new image
def image_classification(request):
    logger.info(f"classify image")
    
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        logger.info(f"image request")

        image_data = image.read()
        image_bytes_io = io.BytesIO(image_data)
        
        image_class = classify.classify_image(image_bytes_io)
        logger.info("Image class:")
        logger.info(image_class)
        if image_class:
                return JsonResponse({'success': True, 'image_class': image_class})
    return JsonResponse({'success': False})



def recipe_list(request):
    recipes = recipe.objects.all()
    return render(request, 'pages/recipe_list.html', {'recipes': recipes})

def get_ingredients(request):
     # Zutaten aus der Datenbank abrufen, bei denen part_of_recipe=False ist
    ingredients = Ingredient.objects.filter(part_of_recipe=False).values_list('description', flat=True)
    
    data = {
        'ingredients': list(ingredients)
    }
    
    return JsonResponse(data)


def delete_ingredient(request):
    
    if request.method == 'POST':
        ingredient_id = request.POST.get('ingredient') 
        logger.info("Zutat:" , ingredient_id)
        ingredient_obj = get_object_or_404(Ingredient, id=ingredient_id)
        ingredient_obj.delete()
        return redirect('ingredients_list') 
    
    return redirect('ingredients_list') 


def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)

        logger.info("--- add_recipe")
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    logger.info(f"Form data before saving: {form.cleaned_data}")
                    form.save()
                    logger.info("Form data saved successfully.")
            except Exception as e:
                logger.error(f"Error saving form data: {str(e)}")
                # Hier können Sie weitere Schritte unternehmen, um den Fehler zu behandeln,
                # z. B. eine Fehlermeldung an den Benutzer anzeigen
                
            
            return redirect('recipe_list')
        else:
            logger.error("form is invalid")
            for field, errors in form.errors.items():
                for error in errors:
                    logger.error(f"Field: {field}, Error: {error}")
    else:
        form = RecipeForm()
        
    # Log the content of the form, whether it's a GET or POST request
    logger.info(f"Form data: {form.data}")
    logger.info(f"Form files: {form.files}")
    
    return render(request, 'pages/add_recipe.html', {'form': form})


def delete_recipe(request, recipe_id):
    recipe_obj = get_object_or_404(recipe, id=recipe_id)
    if request.method == 'POST':
        recipe_obj.delete()
        logger.info("Recipe deleted")
        return redirect('recipe_list') 
    return redirect('recipe_list') 



#def recipe_detail(request, recipe_id):
#    recipe_obj = get_object_or_404(recipe, id=recipe_id)
#    return render(request, 'pages/recipe_detail.html', {'recipe': recipe_obj})

def recipe_detail(request, recipe_id):
    recipe_obj = get_object_or_404(recipe, id=recipe_id)
    
    # all ingredients in recipe
    ingredients = recipe_obj.ingredients.all()
    
    # all available ingredients
    available_ingredients = Ingredient.objects.filter(part_of_recipe=False)

    # check if they are enough
    all_ingredients_available = "true"

    logger.info("Check available ingredients for recipe")

    for ingredient in ingredients:
        
        try:
            logger.info(ingredient.description)
            
            if available_ingredients.get(description=ingredient.description) :
                available_ingredient = available_ingredients.get(description=ingredient.description)
            else:
                all_ingredients_available = "false"
                logger.info(ingredient.description + " is not available")
                break


            # Check if quantity is enough
            if ingredient.weight == 0 and ingredient.quantity > available_ingredient.quantity:
                all_ingredients_available = "false"
                logger.info("Quantity is to low")
                break

            # check if weight is enough
            if ingredient.weight > 0 and ingredient.weight > available_ingredient.weight:
                all_ingredients_available = "false"
                logger.info("Weight is to low")
                break
            
        except Ingredient.DoesNotExist:

                all_ingredients_available = "false"
                pass      
            
    return render(request, 'pages/recipe_detail.html', {'recipe': recipe_obj, 'all_ingredients_available': all_ingredients_available})


def folder_list(request):
    trainset_path = os.path.join(settings.CLASSIFICATION_ROOT, 'trainsets')
    if not os.path.exists(trainset_path):
        # Verzeichnis anlegen, wenn es nicht vorhanden ist
        os.makedirs(trainset_path)
    
    folders = os.listdir(trainset_path)
    folder_data = []
    
    for folder in folders:
        folder_path = os.path.join(trainset_path, folder)
        images = [image for image in os.listdir(folder_path) if image.endswith('.jpeg')]
        folder_data.append({'foldername': folder, 'images': images})
    
    return render(request, 'pages/folder_list.html', {'folder_data': folder_data})

def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        trainset_path = os.path.join(settings.CLASSIFICATION_ROOT, 'trainsets')
        new_folder_path = os.path.join(trainset_path, folder_name)
        
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
    
    return redirect('folder_list')

def delete_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        trainset_path = os.path.join(settings.CLASSIFICATION_ROOT, 'trainsets')
        folder_path = os.path.join(trainset_path, folder_name)
        if os.path.exists(folder_path):
            try:
                #os.rmdir()
                shutil.rmtree(folder_path)
            except Exception as e:
                # Handhaben Sie den Fehler entsprechend
                pass
    return redirect('folder_list')


def upload_image(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        
        images = request.FILES.getlist('image')
        trainset_path = os.path.join(settings.CLASSIFICATION_ROOT, 'trainsets')
        folder_path = os.path.join(trainset_path, folder_name)
        for image in images:
                
            
            image_path = os.path.join(folder_path, image.name)
            
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
    
    return redirect('folder_list')


def cooked_recipe(request, recipe_id):
    recipe_obj = get_object_or_404(recipe, id=recipe_id)
    
    if request.method == 'POST':
        
        ##get all necessary ingredients
        cooked_ingredients = recipe_obj.ingredients.all()
        
        #get all available ingredients
        available_ingredients = Ingredient.objects.filter(part_of_recipe=False)
        
        success = "true"
        logger.info("Reduce available ingredients")
        
        for cooked_ingredient in cooked_ingredients:
            try:
                
                logger.info("Cooked: ", cooked_ingredient.description)
            
                if available_ingredients.get(description=cooked_ingredient.description) :
                    available_ingredient = available_ingredients.get(description=cooked_ingredient.description)
                else:
                    success = "false"
                    logger.info(cooked_ingredient.description + " is not available")
                    break

                if available_ingredient.weight > 0:
                    available_ingredient.weight -= cooked_ingredient.weight  
                    available_ingredient.save()
                else:
                    available_ingredient.quantity -=  cooked_ingredient.quantity  
                    available_ingredient.save()
        
            except Ingredient.DoesNotExist:
                logger.info("Ingredient does not exist: ", Ingredient.description)
                success = "false"
                pass
      
        
        return render(request, 'pages/recipe_detail.html', {'recipe': recipe_obj,'success': success})
    
    return render(request, 'pages/recipe_detail.html', {'recipe': recipe_obj})


def suggested_recipes(request):
    keyword = "kartoffel"  
    recipes = fwl.find_recipes(keyword)
    return render(request, 'pages/suggested_recipes.html', {'recipes': recipes})

def suggested_recipes_keyword(request):
    if request.method == 'POST':
        ingredient = request.POST.get('ingredient', '') 
        recipes = fwl.find_recipes(ingredient)
        return render(request, 'pages/suggested_recipes.html', {'recipes': recipes})
    return redirect('ingredients_list')




##### Settings   
    
    

def settings_site(request):
    
    backup_list = utils.get_backups()
    
    # Die Liste mit Dateinamen und Datum an die HTML-Seite senden    
    return render(request, 'pages/settings.html', {'backup_list': backup_list})


def backup_database(request):
    # Pfade für die Datenbank und das Backup-Verzeichnis.
    database_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    backup_directory = os.path.join(settings.BASE_DIR, 'backup')

    # Erstellen Sie das Backup-Verzeichnis, wenn es nicht existiert.
    os.makedirs(backup_directory, exist_ok=True)

    # Aktuelles Datum und Uhrzeit erhalten
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d_%H-%M-%S")


    backup_file_name = f"db_backup_{current_date}.sqlite3"
    backup_file_path = os.path.join(backup_directory, backup_file_name)


    try:
        # Datenbank-Backup durchführen.
        shutil.copy2(database_path, backup_file_path)

        # Erfolgreiche Antwort zurückgeben, wenn das Backup erfolgreich erstellt wurde.
        # response = f"Database backup created successfully. File saved at: {backup_file_path}"
        return redirect('settings_site')

    except Exception as e:
        # Fehlerantwort zurückgeben, wenn beim Backup ein Fehler aufgetreten ist.
        error_msg = f"Error creating database backup: {e}"
        return HttpResponse(error_msg, status=500)
    
    
def delete_backup(request):
    if request.method == 'POST':
        backup_file = request.POST.get('backup_file')
        backup_file_path = os.path.join(settings.BASE_DIR, 'backup', backup_file)

        try:
            # Backup-Datei löschen.
            os.remove(backup_file_path)
        except Exception as e:
            # Fehlerantwort zurückgeben, wenn beim Löschen ein Fehler aufgetreten ist.
            error_msg = f"Error deleting backup: {e}"
            return HttpResponse(error_msg, status=500)

    return redirect('settings_site')

def restore_database(request):
    if request.method == 'POST':
        backup_file = request.POST.get('backup_file')
        backup_file_path = os.path.join(settings.BASE_DIR, 'backup', backup_file)
        database_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')

        try:
            # Original-Datenbank durch das Backup ersetzen.
            shutil.copy2(backup_file_path, database_path)
        except Exception as e:
            # Fehlerantwort zurückgeben, wenn beim Ersetzen ein Fehler aufgetreten ist.
            error_msg = f"Error replacing database: {e}"
            return HttpResponse(error_msg, status=500)

    return redirect('base')