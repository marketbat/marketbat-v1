# Generated by Django 4.2.3 on 2023-10-23 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bat_app', '0049_alter_signal_order_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signal',
            name='entry_price',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='signal',
            name='stoploss',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='signal',
            name='takeprofit',
            field=models.CharField(max_length=100),
        ),
    ]
