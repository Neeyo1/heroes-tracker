from django import forms
from .models import MapGroup, Map, Hero
from django.contrib.auth.models import User

class MapGroupForm(forms.ModelForm):
    class Meta:
        model = MapGroup
        fields = ['name', 'description']

class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ['name', 'description', 'map_group']

class HeroForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = ['name', 'description', 'lvl', 'maps']