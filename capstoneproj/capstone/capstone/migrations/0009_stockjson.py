# Generated by Django 3.1.6 on 2021-03-19 02:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('capstone', '0008_ownedpackage'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockJSON',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=10, unique=True)),
                ('stock_name', models.CharField(max_length=100)),
                ('info', models.JSONField()),
                ('sector', models.CharField(max_length=30)),
                ('market_cap', models.CharField(max_length=30)),
                ('year_high', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('year_low', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('percentage_change', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('price_change', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('previous_closing_price', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('historic_monthly', models.JSONField(default={})),
                ('historic_yearly', models.JSONField(default={})),
                ('ownedBy', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
