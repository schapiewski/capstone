# Generated by Django 3.1.6 on 2021-03-02 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capstone', '0005_ticker_ownedby'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticker',
            name='ema12',
            field=models.TextField(default='26.76, 34.45, 45.43, 54.56'),
        ),
        migrations.AddField(
            model_name='ticker',
            name='ema26',
            field=models.TextField(default='26.76, 34.45, 45.43, 54.56'),
        ),
        migrations.AddField(
            model_name='ticker',
            name='macd',
            field=models.TextField(default='26.76, 34.45, 45.43, 54.56'),
        ),
        migrations.AddField(
            model_name='ticker',
            name='macd_signal',
            field=models.TextField(default='26.76, 34.45, 45.43, 54.56'),
        ),
        migrations.AddField(
            model_name='ticker',
            name='recommendation',
            field=models.CharField(default='Sell', max_length=10),
        ),
    ]