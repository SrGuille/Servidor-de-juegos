from django.urls import path
from. import main_views
from .games.democracy import democracy_views
from .games.hangman import hangman_views
from .games.roulette import roulette_views

urlpatterns = [
    # Main views
    path('', main_views.login_render, name='login_render'),
    path('ranking_and_prizes/', main_views.ranking_and_prizes_render, name='ranking_and_prizes_render'),
    path('wait_room/', main_views.wait_room_render, name='wait_room_render'),
    path('game_selector/', main_views.game_selector_render, name='game_selector_render'),
    
    path('set_game/', main_views.set_game, name='set_game'),
    path('transition_to_next_game/', main_views.transition_to_next_game, name='transition_to_next_game'),
    
    path('register_player/', main_views.register_player, name='register_player'),
    
    path('get_players_scores/', main_views.get_players_scores, name='get_players_scores'),
    path('get_available_prizes/', main_views.get_available_prizes, name='get_available_prizes'),
    path('create_roulettes/', main_views.create_roulettes, name='create_roulettes'),
    path('send_prize_to_winner/', main_views.send_prize_to_winner, name='send_prize_to_winner'),

    path('get_number_players/', main_views.get_number_players, name='get_number_players'),
    path('get_player_coins/', main_views.get_player_coins, name='get_player_coins'),
    
    path('get_ready_to_join_game/', main_views.get_ready_to_join_game, name='get_ready_to_join_game'),
    path('set_can_players_join/', main_views.set_can_players_join, name='set_can_players_join'),
    path('set_can_players_interact/', main_views.set_can_players_interact, name='set_can_players_interact'),
    
    # Roulette views
    path('roulette_admin/', roulette_views.roulette_admin_render, name='roulette_admin_render'),
    path('roulette_player/', roulette_views.roulette_player_render, name='roulette_player_render'),
    path('send_player_bets/', roulette_views.send_player_bets, name='send_player_bets'),
    path('send_roulette_result/', roulette_views.send_roulette_result, name='send_roulette_result'),

    # Hangman views
    path('hangman_admin/', hangman_views.hangman_admin_render, name='hangman_admin_render'),
    path('hangman_player/', hangman_views.hangman_player_render, name='hangman_player_render'),
    path('create_sentence/', hangman_views.create_sentence, name='create_sentence'),
    path('send_player_guess/', hangman_views.send_player_guess, name='send_player_guess'),
    path('perform_step/', hangman_views.perform_step, name='perform_step'),

    # Democracy views
    path('democracy_admin/', democracy_views.democracy_admin_render, name='democracy_admin_render'),
    path('democracy_player/', democracy_views.democracy_player_render, name='democracy_player_render'),
    path('send_player_move/', democracy_views.send_player_move, name='send_player_move'),
    path('get_democratic_move/', democracy_views.get_democratic_move, name='get_democratic_move'),
    path('get_my_team/', democracy_views.get_my_team, name='get_my_team'),
    path('send_colors_per_second/', democracy_views.send_colors_per_second, name='send_colors_per_second'),
    path('create_teams/', democracy_views.create_teams, name='create_teams'),

]
