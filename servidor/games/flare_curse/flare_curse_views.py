from django.shortcuts import render


def flare_curse_player_render(request):
    return render(request, 'flare_curse/flare_curse_player.html')


def flare_curse_host_render(request):
    """
    Host page with no gameplay controls.
    It only listens to game events and returns to game selector when the game ends.
    """
    return render(request, 'flare_curse/flare_curse_host.html')