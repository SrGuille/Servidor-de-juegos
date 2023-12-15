from django.contrib import admin

# Register your models here.

from .models import Player, Prize, Coins_evolution, Prizes_evolution

admin.site.register(Player)
admin.site.register(Prize)
admin.site.register(Coins_evolution)
admin.site.register(Prizes_evolution)
