from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    ticker = models.CharField(max_length=10)

    def __str__(self):
        return self.ticker


class Package(models.Model):
    package = models.CharField(max_length=20)
    sector = models.CharField(max_length=50)


    def __str__(self):
        return self.package, self.sector

class Sector(models.Model):
    sector_name = models.CharField(max_length=30)
    percent_change = models.CharField(max_length=10)


    def __str__(self):
        return self.sector_name


class Ticker(models.Model):
    ticker = models.CharField(max_length=10)
    stock_name = models.CharField(max_length=100, unique=True)
    ownedBy = models.ManyToManyField(User)
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
    ema12 = models.TextField(default='26.76, 34.45, 45.43, 54.56')
    ema26 = models.TextField(default='26.76, 34.45, 45.43, 54.56')
    macd = models.TextField(default='26.76, 34.45, 45.43, 54.56')
    macd_signal = models.TextField(default='26.76, 34.45, 45.43, 54.56')
    recommendation = models.CharField(max_length=10, default='Sell')

    def __str__(self):
        return '%s' % (self.ticker)
