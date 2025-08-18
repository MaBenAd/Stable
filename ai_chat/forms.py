from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Requis. Entrez une adresse email valide.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les labels et help_text
        self.fields['username'].help_text = 'Requis. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ uniquement.'
        self.fields['password1'].help_text = 'Votre mot de passe doit contenir au moins 8 caractères.'
        self.fields['password2'].help_text = 'Entrez le même mot de passe que précédemment, pour vérification.'
        
        # Ajouter des classes CSS pour le style
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input appearance-none relative block w-full px-3 py-3 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm'})
