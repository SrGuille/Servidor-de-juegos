# Generated by Django 4.1.4 on 2024-12-28 00:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servidor', '0012_rename_last_duel_game_number_player_last_help_game_number_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='last_help_game_number',
            new_name='last_aid_game_number',
        ),
    ]