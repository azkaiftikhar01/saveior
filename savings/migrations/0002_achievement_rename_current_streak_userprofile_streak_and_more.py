# Generated by Django 5.0.2 on 2025-04-24 10:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('points_required', models.IntegerField()),
                ('icon', models.CharField(default='fas fa-trophy', max_length=50)),
            ],
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='current_streak',
            new_name='streak',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='avatar',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='longest_streak',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='theme_preference',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound'), ('JPY', 'Japanese Yen'), ('AUD', 'Australian Dollar'), ('CAD', 'Canadian Dollar'), ('CHF', 'Swiss Franc'), ('CNY', 'Chinese Yuan'), ('INR', 'Indian Rupee'), ('PKR', 'Pakistani Rupee'), ('BRL', 'Brazilian Real'), ('RUB', 'Russian Ruble'), ('ZAR', 'South African Rand'), ('SGD', 'Singapore Dollar'), ('NZD', 'New Zealand Dollar'), ('SEK', 'Swedish Krona'), ('NOK', 'Norwegian Krone'), ('DKK', 'Danish Krone'), ('PLN', 'Polish Złoty'), ('MXN', 'Mexican Peso'), ('KRW', 'South Korean Won')], default='USD', max_length=3),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='achievements',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='achievements',
            field=models.ManyToManyField(blank=True, to='savings.achievement'),
        ),
    ]
