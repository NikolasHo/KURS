from django import forms
from .models import Ingredient, recipe_step, recipe


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'


    

class RecipeForm(forms.Form):
    recipe_name = forms.CharField(label='Rezeptname', max_length=100)
    recipe_description = forms.CharField(label='Beschreibung', widget=forms.Textarea)
    recipe_image = forms.ImageField(label='Bild')
  
    ingredient_description = forms.CharField(label='Name', widget=forms.Textarea)
    ingredient_quantity = forms.CharField(label='Anzahl', widget=forms.Textarea)
    ingredient_weight = forms.CharField(label='Gewicht', widget=forms.Textarea)
    
    
    steps = forms.CharField(label='Schritte', widget=forms.Textarea)
    step_img = forms.ImageField(label='Bild für jeden Schritt')

    def save(self):
        # Speichern Sie das Rezept und die Schritte hier entsprechend Ihrer Logik
        recipe_data = recipe.objects.create(
            headline=self.cleaned_data['recipe_name'],
            description=self.cleaned_data['recipe_description'],
            img=self.cleaned_data['recipe_image']
        )
    
       
        ingredient_descriptions = self.cleaned_data['ingredient_description'].split('\n')
        ingredient_quantitys = self.cleaned_data['ingredient_quantity'].split('\n')
        ingredient_weights = self.cleaned_data['ingredient_weight'].split('\n')
       
        for description, quantity, weight in zip(ingredient_descriptions,ingredient_quantitys,ingredient_weights):
            ingredient_tmp = Ingredient.objects.create(
                description=description,
                quantity=quantity,
                weight=weight,
                part_of_recipe=True
            )
            recipe_data.ingredients.add(ingredient_tmp)
    
        
        steps_data = self.cleaned_data['steps'].split('\n')
        step_images = self.files.getlist('step_img')  # Zugriff auf die Bilder für jeden Schritt
        for step_description, step_image in zip(steps_data, step_images):
            step = recipe_step.objects.create(
                recipe_step_description=step_description,
                recipe_step_img=step_image
            )
            recipe_data.recipe_steps.add(step)

        return recipe_data