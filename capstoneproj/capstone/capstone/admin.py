from django.contrib import admin
from .models import Stock, Ticker, Sector, OwnedPackage

models = [Stock, Ticker, Sector, OwnedPackage]
admin.site.register(models)