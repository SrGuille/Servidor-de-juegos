from django.urls import path
from . import roulette_views, main_views

urlpatterns = [
    path('', main_views.login_render, name='login_render'),
    path('game_selector/', main_views.game_selector_render, name='game_selector_render'),
    path('set_game/', main_views.set_game, name='set_game'),
    path('get_next_game/', main_views.get_next_game, name='get_next_game'),
    path('ranking/', main_views.ranking_render, name='ranking_render'),
    path('register_player/', main_views.register_player, name='register_player'),
    path('get_remaining_interactions/', main_views.get_remaining_interactions, name='get_remaining_interactions'),
    path('get_players_scores/', main_views.get_players_scores, name='get_players_scores'),
    path('get_available_prizes/', main_views.get_available_prizes, name='get_available_prizes'),
    path('create_roulettes/', main_views.create_roulettes, name='create_roulettes'),
    path('get_number_players/', main_views.get_number_players, name='get_number_players'),
    path('get_player_coins/', main_views.get_player_coins, name='get_player_coins'),
    path('dont_listen_client_calls/', main_views.dont_listen_client_calls, name='dont_listen_client_calls'),
    path('send_prize_winner/', main_views.send_prize_winner, name='send_prize_winner'),

    path('roulette_host/', roulette_views.roulette_host_render, name='roulette_host_render'),
    path('roulette_client/', roulette_views.roulette_client_render, name='roulette_client_render'),
    path('send_player_bets/', roulette_views.send_player_bets, name='send_player_bets'),
    path('send_roulette_result/', roulette_views.send_roulette_result, name='send_roulette_result'),
]