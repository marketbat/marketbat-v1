# Generated by Django 4.2.3 on 2023-09-26 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bat_app', '0028_alter_assets_market_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articles',
            name='article_polarity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=100),
        ),
    ]
