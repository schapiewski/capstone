from django.contrib import admin
from .models import Stock, Ticker

models = [Stock, Ticker]
admin.site.register(models)