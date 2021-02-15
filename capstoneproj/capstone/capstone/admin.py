from django.contrib import admin
from .models import Stock, Ticker

myModels = [Stock, Ticker]
admin.site.register(myModels)