# Generated by Django 4.1.4 on 2024-12-27 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servidor', '0011_alter_player_last_duel_game_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='last_duel_game_number',
            new_name='last_help_game_number',
        ),
        migrations.AddField(
            model_name='player',
            name='last_rich_duel_game_number',
            field=models.IntegerField(default=-1),
        ),
    ]
