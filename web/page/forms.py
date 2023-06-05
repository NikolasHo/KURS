from django import forms
from .models import Ingredient

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'

IngredientFormSet = forms.inlineformset_factory(parent_model=None, model=Ingredient, fields=('img', 'description', 'mhd', 'quantity', 'tags'), extra=1, can_delete=False)