# Generated by Django 3.0 on 2019-12-20 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_network_app', '0009_auto_20191219_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='state',
            field=models.IntegerField(default=0),
        ),
    ]
