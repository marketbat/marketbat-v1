# Generated by Django 4.2.3 on 2023-07-07 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bat_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assets',
            name='new_drop',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assets',
            name='trending',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='assets',
            name='alltime_conversation_intensity',
            field=models.CharField(choices=[('Strong', 'Strong'), ('Normal', 'Normal'), ('Weak', 'Weak')], default='Normal', max_length=100),
        ),
        migrations.AlterField(
            model_name='assets',
            name='alltime_sentiment',
            field=models.CharField(choices=[('Bullish', 'Bullish'), ('Bearish', 'Bearish'), ('Neutral', 'Neutral')], default='Neutral', max_length=100),
        ),
        migrations.AlterField(
            model_name='assets',
            name='current_conversation_intensity',
            field=models.CharField(choices=[('Strong', 'Strong'), ('Normal', 'Normal'), ('Weak', 'Weak')], default='Normal', max_length=100),
        ),
        migrations.AlterField(
            model_name='assets',
            name='current_sentiment',
            field=models.CharField(choices=[('Bullish', 'Bullish'), ('Bearish', 'Bearish'), ('Neutral', 'Neutral')], default='Neutral', max_length=100),
        ),
        migrations.AlterField(
            model_name='assets',
            name='month_conversation_intensity',
            field=models.CharField(choices=[('Strong', 'Strong'), ('Normal', 'Normal'), ('Weak', 'Weak')], default='Normal', max_length=100),
        ),
        migrations.AlterField(
            model_name='assets',
            name='month_sentiment',
            field=models.CharField(choices=[('Bullish', 'Bullish'), ('Bearish', 'Bearish'), ('Neutral', 'Neutral')], default='Neutral', max_length=100),
        ),
        migrations.AlterField(
            model_name='assets',
            name='week_conversation_intensity',
            field=models.CharField(choices=[('Strong', 'Strong'), ('Normal', 'Normal'), ('Weak', 'Weak')], default='Normal', max_length=100),
        ),
        migrations.AlterField(
            model_name='assets',
            name='week_sentiment',
            field=models.CharField(choices=[('Bullish', 'Bullish'), ('Bearish', 'Bearish'), ('Neutral', 'Neutral')], default='Neutral', max_length=100),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favorites', models.ManyToManyField(to='bat_app.assets')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
