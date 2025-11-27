# forms.py
from django import forms
from .models import Tag

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['role', 'name']
        widgets = {
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


from .models import MyList

class MyListForm(forms.ModelForm):
    class Meta:
        model = MyList
<<<<<<< HEAD
        fields = ["name", "description", "is_public"]
=======
        fields = ["name", "description", "is_public"]
>>>>>>> e4bf81d (2025_1127_更新)
