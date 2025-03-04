# Generated by Django 4.1.4 on 2024-12-27 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servidor', '0008_player_prizes_earned'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='coins_evolution',
            unique_together={('player', 'game_number')},
        ),
        migrations.AlterUniqueTogether(
            name='prizes_evolution',
            unique_together={('player', 'prize', 'game_number')},
        ),
        migrations.RemoveField(
            model_name='coins_evolution',
            name='date',
        ),
        migrations.RemoveField(
            model_name='prizes_evolution',
            name='date',
        ),
    ]
