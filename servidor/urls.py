from django.urls import path
from . import main_views, roulette_views, hangman_views, democracy_views

urlpatterns = [
    path('', main_views.login_render, name='login_render'),
    path('ranking/', main_views.ranking_render, name='ranking_render'),
    #path('redirect_to_ready_to_play_game/', main_views.redirect_to_ready_to_play_game, name='redirect_to_ready_to_play_game'),
    path('wait/', main_views.wait_render, name='wait_render'),
    path('game_selector/', main_views.game_selector_render, name='game_selector_render'),
    path('set_game/', main_views.set_game, name='set_game'),
    path('transition_to_next_game/', main_views.transition_to_next_game, name='transition_to_next_game'),
    path('register_player/', main_views.register_player, name='register_player'),
    path('get_remaining_interactions/', main_views.get_remaining_interactions, name='get_remaining_interactions'),
    path('get_players_scores/', main_views.get_players_scores, name='get_players_scores'),
    path('get_available_prizes/', main_views.get_available_prizes, name='get_available_prizes'),
    path('create_roulettes/', main_views.create_roulettes, name='create_roulettes'),
    path('get_number_players/', main_views.get_number_players, name='get_number_players'),
    path('get_player_coins/', main_views.get_player_coins, name='get_player_coins'),
    path('ready_to_play_game/', main_views.ready_to_play_game, name='ready_to_play_game'),
    path('not_ready_to_play_game/', main_views.not_ready_to_play_game, name='not_ready_to_play_game'),
    path('get_ready_to_play_game/', main_views.get_ready_to_play_game, name='get_ready_to_play_game'),
    path('send_prize_winner/', main_views.send_prize_winner, name='send_prize_winner'),

    path('roulette_admin/', roulette_views.roulette_admin_render, name='roulette_admin_render'),
    path('roulette_client/', roulette_views.roulette_client_render, name='roulette_client_render'),
    path('send_player_bets/', roulette_views.send_player_bets, name='send_player_bets'),
    path('send_roulette_result/', roulette_views.send_roulette_result, name='send_roulette_result'),

    path('hangman_admin/', hangman_views.hangman_admin_render, name='hangman_admin_render'),
    path('hangman_client/', hangman_views.hangman_client_render, name='hangman_client_render'),
    path('create_sentence/', hangman_views.create_sentence, name='create_sentence'),
    path('send_player_guess/', hangman_views.send_player_guess, name='send_player_guess'),
    path('perform_step/', hangman_views.perform_step, name='perform_step'),

    path('democracy_admin/', democracy_views.democracy_admin_render, name='democracy_admin_render'),
    path('democracy_client/', democracy_views.democracy_client_render, name='democracy_client_render'),
    path('send_player_move/', democracy_views.send_player_move, name='send_player_move'),
    path('get_democratic_move/', democracy_views.get_democratic_move, name='get_democratic_move'),
    path('get_my_team/', democracy_views.get_my_team, name='get_my_team'),
    path('send_colors_per_second/', democracy_views.send_colors_per_second, name='send_colors_per_second'),
    path('create_teams/', democracy_views.create_teams, name='create_teams'),

]
