
import json
import logging
import os
import classification.classificationSettings as classificationSettings
import classification.classify as classify
import classification.classification as classification
import io
import food.fwl as fwl
import shutil
import page.utils as utils 
import random
import uuid
import yaml


from django.shortcuts import render, redirect, get_object_or_404, HttpResponse 
from django.http import HttpResponseServerError, JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Ingredient, recipe
from .forms import IngredientForm
from taggit.models import Tag
from .forms import RecipeForm
from django.db import transaction
from datetime import datetime
from ultralytics import YOLO
from classification.detection import detect_ingredients



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
    if os.path.exists(classificationSettings.CLASSIFICATION_CLASSES_FULLNAME):
       
        with open(classificationSettings.CLASSIFICATION_CLASSES_FULLNAME, 'r') as f:
            AvailableClassNames = json.load(f)
        
        return render(request, 'pages/classification.html', {'AvailableClassNames': AvailableClassNames})
  
    return render(request, 'pages/classification.html')
  
  
def train_network(request):
    if request.method == 'POST':
        result = classification.train_classification_network()
        if os.path.exists(classificationSettings.CLASSIFICATION_CLASSES_FULLNAME):
       
            with open(classificationSettings.CLASSIFICATION_CLASSES_FULLNAME, 'r') as f:
                AvailableClassNames = json.load(f)
        
    
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




### New KI

# Pfad zur Dataset-Konfiguration
DATASET_CONFIG = os.path.join(
    settings.BASE_DIR,
    'classification',
    'yolov5_dataset',
    'dataset.yaml'
)
DATASET_ROOT = os.path.join(
    settings.BASE_DIR,
    'classification',
    'yolov5_dataset'
)

def load_class_names():
    """
    Liest die Klassennamen aus der dataset.yaml
    und gibt sie als Liste zurück.
    """
    with open(DATASET_CONFIG, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg.get('names', [])

def save_class_names(names):
    """
    Speichert die aktualisierte list der Klassennamen in dataset.yaml,
    aktualisiert 'nc' entsprechend.
    """
    data = {
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(names),
        'names': names
    }
    with open(DATASET_CONFIG, 'w') as f:
        yaml.dump(data, f)

def add_class_name(request):
    """
    HAndelt das Hinzufügen einer neuen Klasse über das Web-Formular.
    """
    if request.method == 'POST':
        new_name = request.POST.get('new_class_name', '').strip()
        if not new_name:
            return HttpResponseServerError('Kein Klassenname angegeben.')
        names = load_class_names()
        if new_name in names:
            return HttpResponseServerError('Klasse existiert bereits.')
        names.append(new_name)
        save_class_names(names)
        return redirect('upload_training_image')
    return redirect('upload_training_image')

def upload_training_image(request):
    # Klassenliste dynamisch laden
    class_names = load_class_names()

    if request.method == 'POST':
        # Ausgewählte Klasse und Dateien auslesen
        class_id = int(request.POST['class_name'])
        class_name = class_names[class_id]
        images = request.FILES.getlist('images')

        for img in images:
            # Zufälliges Split: 20 % Val, 80 % Train
            subset = 'val' if random.random() < 0.2 else 'train'

            # Ziel-Ordner erstellen
            img_dir = os.path.join(DATASET_ROOT, 'images', subset)
            os.makedirs(img_dir, exist_ok=True)

            # Eindeutigen Dateinamen generieren
            ext = os.path.splitext(img.name)[1]
            filename = f"{class_name}_{uuid.uuid4().hex}{ext}"

            # Bild speichern
            img_path = os.path.join(img_dir, filename)
            with open(img_path, 'wb+') as f:
                for chunk in img.chunks():
                    f.write(chunk)

            # YOLO-Label (ganze Bildfläche)
            lbl_dir = os.path.join(DATASET_ROOT, 'labels', subset)
            os.makedirs(lbl_dir, exist_ok=True)
            lbl_path = os.path.join(lbl_dir, f"{os.path.splitext(filename)[0]}.txt")
            with open(lbl_path, 'w') as f:
                # class_id x_center y_center width height
                # ganze Bildfläche annotieren: x_center=0.5, y_center=0.5, width=1.0, height=1.0
                f.write(f"{class_id} 0.5 0.5 1.0 1.0\n")

        # Nach Upload wieder zurück zur Upload-Seite
        return redirect('upload_training_image')

    # GET: Formular anzeigen mit dynamischen Klassen
    return render(
        request,
        'pages/upload_training.html',
        {'class_names': load_class_names()}
    )

model_weights = 'yolov5s.pt'


def train_model(request):
    if request.method == 'POST':
        # Hyperparameter aus Formular
        try:
            epochs = int(request.POST.get('epochs', 50))
            imgsz = int(request.POST.get('imgsz', 640))
        except ValueError:
            return HttpResponseServerError('Ungültige Parameter.')

        # YOLO-Train aufrufen
        try:
            model = YOLO(model_weights)
            model.train(
                data=DATASET_CONFIG,
                epochs=epochs,
                imgsz=imgsz,
                project=os.path.join(settings.BASE_DIR, 'runs'),
                name='web-training',
            )
        except Exception as e:
            return HttpResponseServerError(f'Training fehlgeschlagen: {e}')

        return JsonResponse({'success': True, 'message': 'Training abgeschlossen.'})
    # GET: Formular anzeigen
    return render(request, 'pages/train_model.html')




def detect_and_add(request):
    if 'image' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Kein Bild gesendet.'}, status=400)

    dets = detect_ingredients(request.FILES['image'], conf_threshold=0.5)
    if not dets:
        return JsonResponse({'success': False, 'error': 'Kein Modell verfügbar oder keine Erkennung.'})

    added, updated = [], []
    counts = {}
    for d in dets:
        desc = d['class']
        counts[desc] = counts.get(desc, 0) + 1

    for desc, cnt in counts.items():
        obj, created = Ingredient.objects.get_or_create(
            description=desc,
            part_of_recipe=False,
            defaults={'quantity': cnt, 'weight': 0}
        )
        if created:
            added.append(desc)
        else:
            obj.quantity += cnt
            obj.save()
            updated.append(desc)

    return JsonResponse({'success': True, 'added': added, 'updated': updated})

def bulk_add_ingredients(request):
    # GET: Bulk-Erkennungsseite
    return render(request, 'pages/bulk_add_ingredients.html')


def detect_and_list(request):
    if 'image' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Kein Bild.'}, status=400)
    # Inferenz durchführen
    detections = detect_ingredients(request.FILES['image'], conf_threshold=0.5)
    # Klassen zählen
    counts = {}
    for det in detections:
        cls = det['class']
        counts[cls] = counts.get(cls, 0) + 1
    # In Liste umwandeln
    items = [{'class': cls, 'count': count} for cls, count in counts.items()]
    return JsonResponse({'success': True, 'items': items})

def bulk_save_ingredients(request):
    # Parsen der POST-Felder items[i].<field>
    pattern = re.compile(r'^items\[(\d+)\]\.(\w+)$')
    temp = {}
    for key, vals in request.POST.lists():
        m = pattern.match(key)
        if not m:
            continue
        idx = int(m.group(1))
        field = m.group(2)
        value = vals[0]
        temp.setdefault(idx, {})[field] = value

    added, updated = [], []
    # Daten validieren und speichern
    for idx in sorted(temp.keys()):
        data = temp[idx]
        desc = data.get('description')
        if not desc:
            continue
        mhd = data.get('mhd') or None
        quantity = int(data.get('quantity', 1))
        weight = float(data.get('weight', 0))
        tags = [t.strip() for t in data.get('tags', '').split(',') if t.strip()]

        obj, created = Ingredient.objects.get_or_create(
            description=desc,
            part_of_recipe=False,
            defaults={'quantity': quantity, 'weight': weight, 'mhd': mhd}
        )
        if created:
            if hasattr(obj, 'tags'):
                obj.tags.set(tags)
            added.append(desc)
        else:
            obj.quantity += quantity
            if weight:
                obj.weight = weight
            obj.save()
            updated.append(desc)

    return JsonResponse({'success': True, 'added': added, 'updated': updated})


def test_detection(request):
    """
    GET: Rendert die Testseite für Objekterkennung.
    POST: Führt Detection durch und liefert JSON mit den Ergebnissen.
    """
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'Kein Bild.'}, status=400)
        detections = detect_ingredients(request.FILES['image'], conf_threshold=0.5)
        # Ergebnis direkt als JSON zurückgeben
        return JsonResponse({'success': True, 'detections': detections})
    # GET: Seite rendern
    return render(request, 'pages/test_detection.html')