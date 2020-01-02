from django.contrib import admin

from bot.models import SlackUser, MemeTemplate


@admin.register(SlackUser)
class SlackUserAdmin(admin.ModelAdmin):
    pass


@admin.register(MemeTemplate)
class MemeTemplateAdmin(admin.ModelAdmin):
    pass
