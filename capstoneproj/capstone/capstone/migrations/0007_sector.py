# Generated by Django 3.1.6 on 2021-03-10 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capstone', '0006_auto_20210301_2124'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sector_name', models.CharField(max_length=30)),
                ('percent_change', models.CharField(max_length=10)),
            ],
        ),
    ]
