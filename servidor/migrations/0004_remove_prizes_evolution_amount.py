# Generated by Django 4.1.4 on 2023-12-15 01:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servidor', '0003_alter_coins_evolution_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prizes_evolution',
            name='amount',
        ),
    ]
