from django.urls import path
from. import main_views
from .games.democracy import democracy_views
from .games.hangman import hangman_views
from .games.roulette import roulette_views
from .games.gunman import gunman_views
from .games.bnumber import bnumber_views

urlpatterns = [
    # Main views
    path('', main_views.login_render, name='login_render'),
    path('ranking_and_prizes/', main_views.ranking_and_prizes_render, name='ranking_and_prizes_render'),
    path('wait_room/', main_views.wait_room_render, name='wait_room_render'),
    path('game_selector/', main_views.game_selector_render, name='game_selector_render'),
    
    path('set_game/', main_views.set_game, name='set_game'),
    path('transition_to_next_game/', main_views.transition_to_next_game, name='transition_to_next_game'),
    
    path('login_player/', main_views.login_player, name='login_player'),
    path('get_players_names/', main_views.get_players_names, name='get_players_names'),
    path('logout/', main_views.logout, name='logout'),
    
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
    path('init_clock/', democracy_views.init_clock, name='init_clock'),
    path('send_player_move/', democracy_views.send_player_move, name='send_player_move'),
    path('get_democratic_move/', democracy_views.get_democratic_move, name='get_democratic_move'),
    path('get_my_team_democracy/', democracy_views.get_my_team_democracy, name='get_my_team_democracy'),
    path('send_colors_per_second/', democracy_views.send_colors_per_second, name='send_colors_per_second'),
    path('create_teams_democracy/', democracy_views.create_teams_democracy, name='create_teams_democracy'),

    # Gunman views
    path('gunman_admin/', gunman_views.gunman_admin_render, name='gunman_admin_render'),
    path('gunman_player/', gunman_views.gunman_player_render, name='gunman_player_render'),
    path('create_initial_duel/', gunman_views.create_initial_duel, name='create_initial_duel'),
    path('create_special_duel/', gunman_views.create_special_duel, name='create_special_duel'),
    path('send_player_action/', gunman_views.send_player_action, name='send_player_action'),
    path('get_duel_data/', gunman_views.get_duel_data, name='get_duel_data'),
    path('duel_step/', gunman_views.duel_step, name='duel_step'),
    path('special_duel_step/', gunman_views.special_duel_step, name='special_duel_step'),

    # BNumber views
    path('bnumber_admin/', bnumber_views.bnumber_admin_render, name='bnumber_admin_render'),
    path('bnumber_player/', bnumber_views.bnumber_player_render, name='bnumber_player_render'),
    path('create_teams_bnumber/', bnumber_views.create_teams_bnumber, name='create_teams_bnumber'),
    path('get_my_team_bnumber/', bnumber_views.get_my_team_bnumber, name='get_my_team_bnumber'),
    path('send_position/', bnumber_views.send_position, name='send_position'),
    path('get_bnumber_data/', bnumber_views.get_bnumber_data, name='get_bnumber_data'),
    path('finish_bnumber/', bnumber_views.finish_bnumber, name='finish_bnumber'),

    # Economic policy views
    path('decide_call_special_duel_or_santa/', main_views.decide_call_special_duel_or_santa, name='decide_call_special_duel_or_santa'),
    path('balance_inflation_deflation/', main_views.balance_inflation_deflation, name='balance_inflation_deflation')
    
]
