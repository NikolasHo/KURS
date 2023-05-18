from django import forms
from .models import Zutat

class ZutatForm(forms.ModelForm):
    class Meta:
        model = Zutat
        fields = '__all__'