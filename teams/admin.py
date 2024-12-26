from django.contrib import admin
from .models import Team

class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'leader', 'event', 'open')  # Correct field names
    list_filter = ('event', 'open')  # Correct field names
    search_fields = ('team_name', 'leader__username', 'event__name')
    filter_horizontal = ('invited_users',)
    ordering = ('team_name',)

admin.site.register(Team, TeamAdmin)
