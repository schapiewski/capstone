from django.contrib import admin
from .models import Stock, Ticker, Sector, OwnedPackage, StockJSON

models = [Stock, Ticker, Sector, OwnedPackage, StockJSON]
admin.site.register(models)