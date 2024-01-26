from django import forms
from .models import Ingredient, recipe_step, recipe
import logging

logger = logging.getLogger(__name__)

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
    
    step_headline = forms.CharField(label='Schritt', widget=forms.Textarea)
    step_description = forms.CharField(label='Beschreibung', widget=forms.Textarea)
    step_img = forms.ImageField(label='Bild für jeden Schritt', required=False)

    def save(self):
        recipe_data = recipe.objects.create(
            headline=self.cleaned_data['recipe_name'],
            description=self.cleaned_data['recipe_description'],
            img=self.cleaned_data['recipe_image']
        )

        ingredient_descriptions = self.data.getlist('ingredient_description')
        ingredient_quantitys = self.data.getlist('ingredient_quantity')
        ingredient_weights = self.data.getlist('ingredient_weight')

        for description, quantity, weight in zip(ingredient_descriptions, ingredient_quantitys, ingredient_weights):
            ingredient_tmp = Ingredient.objects.create(
                description=description,
                quantity=quantity,
                weight=weight,
                part_of_recipe=True
            )
            recipe_data.ingredients.add(ingredient_tmp)

        step_headlines = self.data.getlist('step_headline')
        step_descriptions = self.data.getlist('step_description')
        step_images = self.files.getlist('step_img')

        for i in range(len(step_headlines)):
            headline = step_headlines[i]
            description = step_descriptions[i]
            image = step_images[i] if i < len(step_images) else None

            step = recipe_step.objects.create(
                recipe_step_description=description,
                recipe_step_headline=headline,
            )

            if image:
                step.recipe_step_img = image
            step.save()
            recipe_data.recipe_steps.add(step)



        return recipe_data

