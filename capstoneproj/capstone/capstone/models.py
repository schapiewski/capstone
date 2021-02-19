from django.db import models


class Stock(models.Model):
    ticker = models.CharField(max_length=10)

    def __str__(self):
        return self.ticker


class Package(models.Model):
    package = models.CharField(max_length=20)
    sector = models.CharField(max_length=50)


    def __str__(self):
        return self.package, self.sector


class Ticker(models.Model):
    ticker = models.CharField(max_length=10)
    stock_name = models.CharField(max_length=100, unique=True)
    sector = models.CharField(max_length=30)
    market_cap = models.CharField(max_length=30)
    current_price = models.DecimalField(decimal_places=2, max_digits=10000)
    previous_closing_price = models.DecimalField(decimal_places=2, max_digits=10000)
    percentage_change = models.DecimalField(decimal_places=2, max_digits=10000)
    year_high = models.DecimalField(decimal_places=2, max_digits=10000)
    year_low = models.DecimalField(decimal_places=2, max_digits=10000)
    price_change = models.DecimalField(decimal_places=2, max_digits=10000)

    def __str__(self):
        return '%s' % (self.ticker)
