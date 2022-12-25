from django.urls import path
from . import roulette_views, main_views

urlpatterns = [
    path('', main_views.index_render, name='index_render'),
    path('game_selector/', main_views.game_selector_render, name='game_selector_render'),
    path('set_game/', main_views.set_game, name='set_game'),
    path('get_active_game/', main_views.get_active_game, name='get_active_game'),
    path('ranking/', main_views.ranking_render, name='ranking_render'),
    path('register_player/', main_views.register_player, name='register_player'),
    path('get_ranking/', main_views.get_ranking, name='get_ranking'),
    path('get_pie_chart/', main_views.get_pie_chart, name='get_pie_chart'),
    path('get_number_players/', main_views.get_number_players, name='get_number_players'),
    path('get_player_coins/', main_views.get_player_coins, name='get_player_coins'),

    path('roulette_host/', roulette_views.roulette_host_render, name='roulette_host_render'),
    path('roulette_client/', roulette_views.roulette_client_render, name='roulette_client_render'),
    path('send_player_bets/', roulette_views.send_player_bets, name='send_player_bets'),
    path('get_remaining_bets/', roulette_views.get_remaining_bets, name='get_remaining_bets'),
    path('roulette_is_spinning/', roulette_views.roulette_is_spinning, name='roulette_is_spinning'),
    path('send_roulette_result/', roulette_views.send_roulette_result, name='send_roulette_result'),
]