
import json
import logging
import os
import classification.classification_settings as classification_settings
import classification.classify as classify
import classification.classification as classification
import io
import food.fwl as fwl

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse 
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Ingredient, recipe
from .forms import IngredientForm
from taggit.models import Tag
from .forms import RecipeForm

logger = logging.getLogger(__name__)

# Create your views here.
###urls
def base(request):
    return render(request, 'base.html', {})


def ingredients_list(request):
    ingredients = Ingredient.objects.all()
    used_tags = Tag.objects.all()
    
    return render(request, 'pages/ingredients_list.html', {'ingredients': ingredients, 'used_tags': used_tags})


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
    with open(classification_settings.CLASSIFICATION_CLASSES_FULLNAME, 'r') as f:
        AvailableClassNames = json.load(f)
        
        
        if request.method == 'POST':
            success = train_network(request)
        else:
            success = None    
            
            return render(request, 'pages/classification.html', {'AvailableClassNames': AvailableClassNames,'success': success})
  
def train_network(request):

    result = classification.train_classification_network()
    
    return HttpResponse(result)  # Hier wird eine HttpResponse-Instanz zurückgegeben




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


def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)

        logger.info(f"--- add_recipe")
        
        if form.is_valid():

            form.save()
            
            return redirect('recipe_list')
    else:
        form = RecipeForm()
    return render(request, 'pages/add_recipe.html', {'form': form})


def delete_recipe(request, recipe_id):
    recipe_obj = get_object_or_404(recipe, id=recipe_id)
    logger.info("Try to delete recipe")
    if request.method == 'POST':
        recipe_obj.delete()
        logger.info("Recipe deleted")
        return redirect('recipe_list') 
    
    return render(request, 'pages/recipe_list.html', {'recipe': recipe_obj})



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

def upload_image(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        image = request.FILES['image']
        
        trainset_path = os.path.join(settings.CLASSIFICATION_ROOT, 'trainsets')
        folder_path = os.path.join(trainset_path, folder_name)
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