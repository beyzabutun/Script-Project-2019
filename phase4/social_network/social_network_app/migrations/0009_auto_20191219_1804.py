# Generated by Django 3.0 on 2019-12-19 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_network_app', '0008_auto_20191219_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrow',
            name='rate',
            field=models.IntegerField(null=True),
        ),
    ]
