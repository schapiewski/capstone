from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth.models import User
from .models import Stock

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UpdateInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class StockForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ["ticker"]