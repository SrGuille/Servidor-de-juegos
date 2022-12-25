from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register_player/', views.register_player, name='register_player'),
    path('roulette/', views.roulette, name='roulette'),
    path('roulette_bet/', views.roulette_bet, name='roulette_bet'),
    path('send_bets/', views.send_bets, name='send_bets'),
    path('get_ranking/', views.get_ranking, name='get_ranking'),
    path('get_player_coins/', views.get_player_coins, name='get_player_coins'),
    path('get_number_players/', views.get_number_players, name='get_number_players'),
    path('get_remaining_bets/', views.get_remaining_bets, name='get_remaining_bets'),
    path('send_roulette_result/', views.send_roulette_result, name='send_roulette_result'),
    path('ranking/', views.ranking, name='ranking'),
    path('get_pie_chart/', views.get_pie_chart, name='get_pie_chart'),
]