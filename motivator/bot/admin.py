from django.contrib import admin

from bot.models import SlackUser


@admin.register(SlackUser)
class SlackUserAdmin(admin.ModelAdmin):
    pass
