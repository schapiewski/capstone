from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth.models import User
from .models import Stock, Package, Ticker

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
		model = Ticker
		fields = ["ticker"]


class PackageForm(forms.ModelForm):
	class Meta:
		model = Package
		fields = ['package', 'sector']