# Generated by Django 4.2.3 on 2023-07-11 08:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bat_app', '0008_alter_assets_market_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assets',
            name='market_price',
        ),
    ]
