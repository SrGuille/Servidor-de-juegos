# Generated by Django 4.1.4 on 2024-12-26 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servidor', '0006_player_in_duel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='in_duel',
        ),
        migrations.AddField(
            model_name='player',
            name='rounds_since_last_duel',
            field=models.IntegerField(default=0),
        ),
    ]
