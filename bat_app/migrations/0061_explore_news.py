# Generated by Django 4.2.3 on 2023-10-26 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bat_app', '0060_explore'),
    ]

    operations = [
        migrations.AddField(
            model_name='explore',
            name='news',
            field=models.TextField(blank=True),
        ),
    ]
