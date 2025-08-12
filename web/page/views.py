
### imports
import json
import logging
import os
import io
import food.fwl as fwl
import shutil
import page.utils as utils 
import random
import uuid
import yaml
import re
import glob

### from django imports
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse 
from django.http import HttpResponseServerError, JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Ingredient, recipe
from .forms import IngredientForm
from taggit.models import Tag
from .forms import RecipeForm
from django.db import transaction
from datetime import datetime
from ultralytics import YOLO
from classification.detection import detect_ingredients



logger = logging.getLogger(__name__)

###urls
def base(request):
    return render(request, 'base.html', {})


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



def detect_ingredients_editable(request):
    if request.method == 'POST' and 'image' in request.FILES:
        # Schritt 1: Bild verarbeiten und Objekte erkennen
        detections = detect_ingredients(request.FILES['image'], conf_threshold=0.5)

          # Schritt 2: Gruppieren und zählen
        counts = {}
        for det in detections:
            cls = det['class']
            counts[cls] = counts.get(cls, 0) + 1

        # Schritt 3: Daten an Template übergeben
        detected_items = [{'description': desc, 'quantity': count} for desc, count in counts.items()]
        return render(request, 'pages/add_ingredients_editable.html', {'detected_items': detected_items})

    return render(request, 'pages/add_ingredients_editable.html')

def save_edited_ingredients(request):
    if request.method == 'POST':
        pattern = re.compile(r'^items\[(\d+)\]\.(\w+)$')
        temp = {}

        for key, values in request.POST.lists():
            match = pattern.match(key)
            if not match:
                continue
            idx = int(match.group(1))
            field = match.group(2)
            temp.setdefault(idx, {})[field] = values[0]

        added, updated = [], []

        for idx in sorted(temp.keys()):
            data = temp[idx]
            desc = data.get('description')
            if not desc:
                continue

            quantity = int(data.get('quantity', 1))
            weight = float(data.get('weight', 0))

            obj, created = Ingredient.objects.get_or_create(
                description=desc,
                part_of_recipe=False,
                defaults={'quantity': quantity, 'weight': weight}
            )

            if created:
                added.append(desc)
            else:
                obj.quantity += quantity
                obj.save()
                updated.append(desc)

        return render(request, 'pages/add_ingredients_editable.html', {
            'saved': True,
            'added': added,
            'updated': updated
        })

    return redirect('add_ingredients_editable')


##### recipes

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

# Global debug print (only outputs if DEBUG is True)
def debug_print(message):
    if settings.DEBUG:
        print(message)

# Dataset configuration and root path
DATASET_CONFIG = os.path.join(settings.BASE_DIR, 'classification', 'yolov5_dataset', 'dataset.yaml')
DATASET_ROOT = os.path.join(settings.BASE_DIR, 'classification', 'yolov5_dataset')


def load_class_names():
    """Load class names from dataset.yaml."""
    debug_print("Loading class names from dataset config.")
    with open(DATASET_CONFIG, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg.get('names', [])


def save_class_names(names):
    """Save updated class names to dataset.yaml, including class count."""
    debug_print(f"Saving {len(names)} class names to config.")
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
    Handle adding a new class name via POST from the web form.

    This view updates the YOLO dataset configuration (dataset.yaml)
    by appending a new class name and updating the class count (nc).
    """
    if request.method == 'POST':
        # Get the submitted class name from the form, remove leading/trailing whitespace
        new_name = request.POST.get('new_class_name', '').strip()

        # Validate that the name is not empty
        if not new_name:
            return HttpResponseServerError('No class name provided.')

        # Load the existing class names from dataset.yaml
        names = load_class_names()

        # Check if the class already exists
        if new_name in names:
            return HttpResponseServerError('Class already exists.')

        # Append the new class and save the updated config
        names.append(new_name)
        save_class_names(names)

        # Debug message (only shows in development)
        debug_print(f"Added new class: {new_name}")

        # Redirect user to the image upload page
        return redirect('upload_training_image')

    # If not a POST request, simply redirect to the upload page
    return redirect('upload_training_image')



def upload_training_image(request):
    """
    Handles uploading of training images through a web form.
    Saves images into the correct YOLO folder structure,
    and generates corresponding label files using full-image annotations.
    """
    # Load class names from the dataset config
    class_names = load_class_names()

    if request.method == 'POST':

        # Get uploaded images from the form
        images = request.FILES.getlist('images')

        for img in images:
            # Randomly assign to 'train' (80%) or 'val' (20%) set
            subset = 'val' if random.random() < 0.2 else 'train'

            # Build target directory path for images
            img_dir = os.path.join(DATASET_ROOT, 'images', subset)
            os.makedirs(img_dir, exist_ok=True)  # Ensure directory exists

            # Generate a unique filename for the image: **nur UUID**, keine Klasse
            ext = os.path.splitext(img.name)[1]  # Keep original extension
            filename = f"{uuid.uuid4().hex}{ext}"
            img_path = os.path.join(img_dir, filename)

            # Save the uploaded image to the target directory
            debug_print(f"Saving image to: {img_path}")
            with open(img_path, 'wb+') as f:
                for chunk in img.chunks():  # Django handles chunked upload
                    f.write(chunk)

            # Prepare the corresponding YOLO label directory
            lbl_dir = os.path.join(DATASET_ROOT, 'labels', subset)
            os.makedirs(lbl_dir, exist_ok=True)  # Ensure label directory exists

            # Label filename matches image filename (with .txt extension)
            lbl_path = os.path.join(lbl_dir, f"{os.path.splitext(filename)[0]}.txt")

            # Write YOLO label:
            # class_id x_center y_center width height
            # Here: entire image is the bounding box (0.5, 0.5, 1.0, 1.0)
            with open(lbl_path, 'w') as f:
                f.write(f"0 0.5 0.5 1.0 1.0\n")

            debug_print(f"Label saved to: {lbl_path}")

        # After upload, redirect back to the same page (clean form)
        return redirect('upload_training_image')

    # GET request: Render the form page with current class list
    return render(request, 'pages/upload_training.html', {'class_names': class_names})


def is_custom_annotated(label_path):
    """
    Checks whether a YOLO label file contains a bounding box
    that is NOT the full image.
    """
    if not os.path.exists(label_path):
        return False

    try:
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                _, x, y, w, h = map(float, parts)
                # Full image box is typically w = 1.0, h = 1.0
                if w < 0.99 or h < 0.99:
                    return True
    except Exception as e:
        print("[ANNOTATION CHECK] Failed to read label:", label_path, e)

    return False



def annotate_image(request):
    """
    List all existing images for annotation and mark annotated ones,
    with optional filters by class and annotation state.
    """
    class_names = load_class_names()

    selected_class = (request.GET.get('cls') or '').strip()
    annotated_filter = request.GET.get('annotated', 'all')

    image_paths = []
    for subset in ['train', 'val']:
        img_dir = os.path.join(DATASET_ROOT, 'images', subset)
        label_dir = os.path.join(DATASET_ROOT, 'labels', subset)

        for img_path in glob.glob(os.path.join(img_dir, '*.*')):
            filename = os.path.basename(img_path)
            rel_path = os.path.relpath(img_path, settings.MEDIA_ROOT).replace("\\", "/")
            label_path = os.path.join(label_dir, os.path.splitext(filename)[0] + ".txt")

            inferred_class = ''
            if os.path.exists(label_path):
                try:
                    with open(label_path, 'r') as lf:
                        first = lf.readline().strip().split()
                        if len(first) >= 1:
                            cls_id = int(first[0])
                            if 0 <= cls_id < len(class_names):
                                inferred_class = class_names[cls_id]
                except Exception:
                    inferred_class = ''

            annotated = is_custom_annotated(label_path)

            if selected_class and inferred_class != selected_class:
                continue
            if annotated_filter == 'yes' and not annotated:
                continue
            if annotated_filter == 'no' and annotated:
                continue

            image_paths.append({
                'path': os.path.join('media', rel_path),
                'subset': subset,
                'filename': filename,
                'is_annotated': annotated,
                'inferred_class': inferred_class,
            })

    # --- NEU: Pagination ---
    per_page = int(request.GET.get('per_page', 24))  # Standard: 24 pro Seite
    paginator = Paginator(image_paths, per_page)
    page_number = request.GET.get('page', 1)

    try:
        images_page = paginator.page(page_number)
    except PageNotAnInteger:
        images_page = paginator.page(1)
    except EmptyPage:
        images_page = paginator.page(paginator.num_pages)

    # Querystring ohne "page" für die Pager-Links
    qs = request.GET.copy()
    qs.pop('page', None)
    base_qs = qs.urlencode()

    per_page_options = [10, 25, 50, 100, 200]

    return render(request, 'pages/annotate_image.html', {
        'class_names': class_names,
        'images_page': images_page,
        'total_images': paginator.count,
        'selected_class': selected_class,
        'annotated_filter': annotated_filter,
        'per_page': per_page,
        'per_page_options': per_page_options,  # <--- hier
        'base_qs': base_qs,
    })





CLASS_NAMES = load_class_names()

@csrf_exempt
def upload_annotated_image_existing(request):
    """
    Save annotations for an existing image in the dataset.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})

    filename = request.POST.get('filename')
    subset = request.POST.get('subset')
    boxes_json = request.POST.get('boxes')

    print("[ANNOTATE_EXISTING] Request received")
    print("  filename:", filename)
    print("  subset:", subset)
    print("  boxes_raw (JSON):", (boxes_json[:100] + '...') if boxes_json else None)

    if not filename or not subset or not boxes_json:
        print("[ANNOTATE_EXISTING] ❌ Missing fields")
        return JsonResponse({'success': False, 'message': 'Missing data'})

    try:
        box_lines = json.loads(boxes_json)
        print("[ANNOTATE_EXISTING] ✅ Parsed boxes:", box_lines)
    except Exception as e:
        print("[ANNOTATE_EXISTING] ❌ JSON parsing error:", e)
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})

    img_path = os.path.join(DATASET_ROOT, 'images', subset, filename)
    print("  Looking for image at:", img_path)

    if not os.path.exists(img_path):
        print("[ANNOTATE_EXISTING] ❌ Image not found!")
        return JsonResponse({'success': False, 'message': 'Image not found'})

    # Ziel-Labeldatei
    label_dir = os.path.join(DATASET_ROOT, 'labels', subset)
    os.makedirs(label_dir, exist_ok=True)
    label_path = os.path.join(label_dir, f"{os.path.splitext(filename)[0]}.txt")

    # Default-Klasse bestimmen:
    # 1) Falls per POST mitgegeben: class_id verwenden
    # 2) Sonst, falls bestehende Labeldatei: deren erste class_id als Default
    default_class_id = request.POST.get('class_id')
    if default_class_id is not None and str(default_class_id).isdigit():
        default_class_id = int(default_class_id)
    else:
        default_class_id = None
        if os.path.exists(label_path):
            try:
                with open(label_path, 'r') as lf:
                    first = lf.readline().strip().split()
                    if len(first) >= 1 and first[0].isdigit():
                        default_class_id = int(first[0])
            except Exception:
                pass

    try:
        with open(label_path, 'w') as f:
            for line in box_lines:
                parts = line.strip().split()
                if len(parts) == 5:
                    # [class_id x y w h] → Klasse übernehmen, nichts überschreiben
                    cls_id, x, y, w, h = parts
                elif len(parts) == 4:
                    # [x y w h] → Klasse fehlt; Default verwenden
                    if default_class_id is None:
                        print("[ANNOTATE_EXISTING] ❌ class_id missing for a box without class.")
                        return JsonResponse({'success': False, 'message': 'class_id missing for boxes without class.'})
                    x, y, w, h = parts
                    cls_id = str(default_class_id)
                else:
                    print(f"[ANNOTATE_EXISTING] ❌ Invalid line skipped: {line}")
                    continue

                final_line = f"{cls_id} {x} {y} {w} {h}"
                f.write(final_line + "\n")
                print("[ANNOTATE_EXISTING] ➤ Saved:", final_line)

        print(f"[ANNOTATE_EXISTING] ✅ File saved at: {label_path}")
    except Exception as e:
        print("[ANNOTATE_EXISTING] ❌ Failed to write label file:", e)
        return JsonResponse({'success': False, 'message': 'Failed to save label'})

    return JsonResponse({'success': True, 'message': 'Annotation saved'})



model_weights = 'yolov5s.pt'

def train_model(request):
    """
    Handle training of a YOLO model using parameters submitted via a web form.

    This view:
    - Accepts POST requests with training hyperparameters
    - Deletes the previous training output (if exists)
    - Initializes a YOLO model and starts training
    """
    if request.method == 'POST':
        try:
            # Read hyperparameters from the form (with fallback defaults)
            epochs = int(request.POST.get('epochs', 50))       # Number of epochs
            imgsz = int(request.POST.get('imgsz', 640))        # Image size

            debug_print(f"Training requested: {epochs} epochs, image size {imgsz}")
        except ValueError:
            # Handle invalid form input
            return HttpResponseServerError('Invalid parameters.')

        try:
            # Remove previous training output directory, if it exists
            output_dir = os.path.join(settings.BASE_DIR, 'runs', 'web-training')
            if os.path.exists(output_dir):
                debug_print(f"Removing previous training output at: {output_dir}")
                shutil.rmtree(output_dir)

            # Initialize the YOLO model with pretrained weights
            model = YOLO(model_weights)
            debug_print("Model initialized. Starting training...")

            # Start training
            model.train(
                data=DATASET_CONFIG,  # Path to dataset.yaml
                epochs=epochs,
                imgsz=imgsz,
                project=os.path.join(settings.BASE_DIR, 'runs'),
                name='web-training',
                # exist_ok not needed since we remove the folder before
            )
        except Exception as e:
            # Catch and report training errors
            debug_print(f"Training failed: {e}")
            return HttpResponseServerError(f'Training failed: {e}')

        # Return success response
        return JsonResponse({'success': True, 'message': 'Training completed.'})

    # GET: Render the training form page
    return render(request, 'pages/train_model.html')



def detect_and_add(request):
    """
    Detect ingredients from an uploaded image and update the database accordingly.

    This view performs the following:
    - Accepts an image via POST request
    - Runs object detection on the image
    - Adds new ingredients or updates existing ones based on detected classes
    - Returns a JSON response indicating which ingredients were added or updated
    """
    # Check if an image file was included in the request
    if 'image' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No image uploaded.'}, status=400)

    # Run detection on the uploaded image using YOLO model
    detections = detect_ingredients(request.FILES['image'], conf_threshold=0.5)

    # Handle detection failure or missing model
    if not detections:
        return JsonResponse({'success': False, 'error': 'No model available or no detections.'})

    added, updated = []  # Lists to track changes
    counts = {}          # Dictionary to count how often each class was detected

    # Count occurrences of each detected class
    for det in detections:
        desc = det['class']
        counts[desc] = counts.get(desc, 0) + 1

    # Add new ingredients or update existing ones in the database
    for desc, count in counts.items():
        obj, created = Ingredient.objects.get_or_create(
            description=desc,
            part_of_recipe=False,
            defaults={'quantity': count, 'weight': 0}  # Default weight if not provided
        )

        if created:
            # New ingredient was added
            added.append(desc)
            debug_print(f"Added ingredient: {desc}")
        else:
            # Ingredient already exists: update quantity
            obj.quantity += count
            obj.save()
            updated.append(desc)
            debug_print(f"Updated ingredient: {desc}")

    # Return the result as JSON
    return JsonResponse({'success': True, 'added': added, 'updated': updated})
def bulk_add_ingredients(request):
    """
    Render the page for bulk image upload and detection.

    This view simply serves the HTML template that allows users
    to upload multiple images for detection and processing.
    """
    return render(request, 'pages/bulk_add_ingredients.html')


def detect_and_list(request):
    """
    Perform object detection on an uploaded image and return a class-wise summary.

    This view:
    - Accepts an image via POST
    - Detects objects using the YOLO model
    - Counts how many times each class appears
    - Returns the result as a list of {class, count} entries
    """
    if 'image' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No image.'}, status=400)

    # Run object detection
    detections = detect_ingredients(request.FILES['image'], conf_threshold=0.5)

    counts = {}
    # Count each detected class
    for det in detections:
        cls = det['class']
        counts[cls] = counts.get(cls, 0) + 1

    # Convert counts to list format for response
    items = [{'class': cls, 'count': count} for cls, count in counts.items()]
    debug_print(f"Detection summary: {items}")

    return JsonResponse({'success': True, 'items': items})


def bulk_save_ingredients(request):
    """
    Process form submission for bulk ingredient creation or update.

    This view:
    - Parses the incoming form fields structured as items[i].<field>
    - Extracts all values for each ingredient (description, mhd, quantity, weight, tags)
    - Adds new ingredients or updates existing ones in the database
    - Returns which items were added or updated
    """
    # Regex pattern to match form keys like items[0].description, items[1].weight, etc.
    pattern = re.compile(r'^items\[(\d+)\]\.(\w+)$')
    temp = {}

    # Group all fields by their item index
    for key, values in request.POST.lists():
        match = pattern.match(key)
        if not match:
            continue
        idx = int(match.group(1))         # Index number of the ingredient
        field = match.group(2)            # Field name (e.g. description, weight)
        temp.setdefault(idx, {})[field] = values[0]

    added, updated = [], []

    # Process each indexed item
    for idx in sorted(temp.keys()):
        data = temp[idx]
        desc = data.get('description')
        if not desc:
            continue  # Skip entries without a description

        # Extract and clean values
        mhd = data.get('mhd') or None  # Best-before date (optional)
        quantity = int(data.get('quantity', 1))
        weight = float(data.get('weight', 0))
        tags = [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()]

        # Try to find an existing ingredient or create a new one
        obj, created = Ingredient.objects.get_or_create(
            description=desc,
            part_of_recipe=False,
            defaults={
                'quantity': quantity,
                'weight': weight,
                'mhd': mhd
            }
        )

        if created:
            # If new, optionally assign tags
            if hasattr(obj, 'tags'):
                obj.tags.set(tags)
            added.append(desc)
            debug_print(f"Added ingredient via bulk: {desc}")
        else:
            # Update existing ingredient
            obj.quantity += quantity
            if weight:
                obj.weight = weight
            obj.save()
            updated.append(desc)
            debug_print(f"Updated ingredient via bulk: {desc}")

    # Return success response with details
    return JsonResponse({'success': True, 'added': added, 'updated': updated})


# oben steht bereits: from classification.detection import detect_ingredients

def test_detection(request):
    """
    Handle image upload for testing the object detection model.
    """
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No image.'}, status=400)

        detections, data_url = detect_ingredients(request.FILES['image'], conf_threshold=0.5, return_image=True)

        return JsonResponse({
            'success': True,
            'detections': detections,
            'image': data_url
        })

    return render(request, 'pages/test_detection.html')



