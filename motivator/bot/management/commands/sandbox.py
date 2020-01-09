import json

from django.core.management import BaseCommand

from bot.models import MemeInstance, MemeTemplate
from bot.tasks import SyncTrelloBoard, ActionReminderDispatchTask


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        #MemeInstance.create_from_template(MemeTemplate.objects.first(), [])
        SyncTrelloBoard().run()
        ActionReminderDispatchTask().run()
