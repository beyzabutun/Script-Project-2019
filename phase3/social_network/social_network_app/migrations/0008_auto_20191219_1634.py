# Generated by Django 3.0 on 2019-12-19 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_network_app', '0007_auto_20191219_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrow',
            name='rate',
            field=models.IntegerField(default=0),
        ),
    ]
