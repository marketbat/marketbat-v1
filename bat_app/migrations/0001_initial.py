# Generated by Django 4.2.3 on 2023-07-07 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('symbol', models.CharField(max_length=100)),
                ('avatar', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('Forex', 'Forex'), ('Cryptocurrency', 'Cryptocurrency'), ('Stocks', 'Stocks'), ('Bonds', 'Bonds'), ('Commodities', 'Commodities'), ('Indices', 'Indices'), ('Exchange-Traded Funds', 'Exchange-Traded Funds'), ('Real Estate Investment Trusts', 'Real Estate Investment Trusts'), ('Non-Fungible Tokens', 'Non-Fungible Tokens'), ('Others', 'Others')], default='Others', max_length=100)),
                ('current_conversation_volume', models.IntegerField(default=0)),
                ('current_conversation_intensity', models.CharField(choices=[('STRONG', 'STRONG'), ('NORMAL', 'NORMAL'), ('WEAK', 'WEAK')], default='NEUTRAL', max_length=100)),
                ('current_sentiment', models.CharField(choices=[('BULLISH', 'BULLISH'), ('BEARISH', 'BEARISH'), ('NEUTRAL', 'NEUTRAL')], default='NEUTRAL', max_length=100)),
                ('week_conversation_volume', models.IntegerField(default=0)),
                ('week_conversation_intensity', models.CharField(choices=[('STRONG', 'STRONG'), ('NORMAL', 'NORMAL'), ('WEAK', 'WEAK')], default='NEUTRAL', max_length=100)),
                ('week_sentiment', models.CharField(choices=[('BULLISH', 'BULLISH'), ('BEARISH', 'BEARISH'), ('NEUTRAL', 'NEUTRAL')], default='NEUTRAL', max_length=100)),
                ('month_conversation_volume', models.IntegerField(default=0)),
                ('month_sentiment', models.CharField(choices=[('BULLISH', 'BULLISH'), ('BEARISH', 'BEARISH'), ('NEUTRAL', 'NEUTRAL')], default='NEUTRAL', max_length=100)),
                ('month_conversation_intensity', models.CharField(choices=[('STRONG', 'STRONG'), ('NORMAL', 'NORMAL'), ('WEAK', 'WEAK')], default='NEUTRAL', max_length=100)),
                ('alltime_conversation_volume', models.IntegerField(default=0)),
                ('alltime_conversation_intensity', models.CharField(choices=[('STRONG', 'STRONG'), ('NORMAL', 'NORMAL'), ('WEAK', 'WEAK')], default='NEUTRAL', max_length=100)),
                ('alltime_sentiment', models.CharField(choices=[('BULLISH', 'BULLISH'), ('BEARISH', 'BEARISH'), ('NEUTRAL', 'NEUTRAL')], default='NEUTRAL', max_length=100)),
            ],
        ),
    ]
