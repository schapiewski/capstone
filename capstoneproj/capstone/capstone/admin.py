from django.contrib import admin
from .models import Stock, Ticker, Sector

models = [Stock, Ticker, Sector]
admin.site.register(models)