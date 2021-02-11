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