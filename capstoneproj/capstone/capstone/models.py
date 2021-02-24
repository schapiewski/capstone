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
    close = models.TextField(default='26.76, 34.45, 45.43, 54.56')
    open = models.TextField(default='28.76, 36.45, 44.43, 56.56')
    high = models.TextField(default='28.76, 38.45, 48.43, 58.56')
    low = models.TextField(default='22.76, 32.45, 42.43, 52.56')
    index = models.TextField(default='2021-02-21, 2021-02-20, 2021-02-19, 2021-02-18')
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
