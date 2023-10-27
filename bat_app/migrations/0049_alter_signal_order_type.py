# Generated by Django 4.2.3 on 2023-10-23 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bat_app', '0048_signal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signal',
            name='order_type',
            field=models.CharField(choices=[('Buy', 'Buy'), ('Sell', 'Sell'), ('Buy Stop', 'Buy Stop'), ('Sell Stop', 'Sell Stop'), ('Buy Limit', 'Buy Limit'), ('Sell Limit', 'Sell Limit')], max_length=100),
        ),
    ]
