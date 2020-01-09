import random
import uuid
from datetime import datetime
from io import BytesIO

from typing import List

from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Subquery, OuterRef, Value
from django.db.models.functions import Coalesce

from bot.draw_utils import overlay_text
from bot.slack import client


class SlackUser(AbstractUser):
    slack_user_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    trello_id = models.CharField(max_length=24, null=True, blank=True, unique=True)

    has_notification_enabled = models.BooleanField(default=True)

    @classmethod
    def create_from_ids(cls, slack_id, trello_id):
        user_info = client.users_info(user=slack_id)['user']
        user = cls(
            slack_user_id=slack_id,
            trello_id=trello_id,
            username=user_info['name'],
            first_name=user_info['profile'].get('first_name', ''),
            last_name=user_info['profile'].get('last_name', '')
        )
        user.set_unusable_password()
        user.save()
        return user

    def generate_meme(self):
        lists = self.cards.values_list('list__trello_id', flat=True)
        template_candidates = []
        for template in MemeTemplate.objects.best_candidates(self):
            if set(template.required_lists.values_list('trello_id', flat=True)).issubset(set(lists)):
                template_candidates.append(template)

        if template_candidates:
            picked_template = template_candidates[0]
            cards = []
            for list_id in picked_template.required_lists.values_list('trello_id', flat=True):
                cards.append(random.choice(
                    list(self.cards.filter(list__trello_id=list_id))
                ))
            return MemeInstance.create_from_template(self, picked_template, cards)

    def __str__(self):
        return f'{self.username} ({self.slack_user_id})'


class TrelloList(models.Model):
    trello_id = models.CharField(max_length=128)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class TrelloCard(models.Model):
    trello_id = models.CharField(max_length=128)
    list = models.ForeignKey('bot.TrelloList', related_name='cards', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    assignees = models.ManyToManyField('bot.SlackUser', related_name='cards')

    def __str__(self):
        return self.name


class MemeTemplateQuerySet(models.QuerySet):
    def with_latest_use_for_user(self, user):
        return self.annotate(
            latest_use=Coalesce(Subquery(
                MemeInstance.objects.filter(template=OuterRef('pk'), receiver=user).order_by('-date_created').values('date_created')[:1]
            ), Value(datetime(day=1, month=1, year=1970)))
        )

    def best_candidates(self, user):
        return self.with_latest_use_for_user(user).order_by('latest_use')


class MemeTemplate(models.Model):
    template = models.ImageField(null=True, upload_to='memes')
    required_lists = models.ManyToManyField('bot.TrelloList', related_name='template')
    text_config = JSONField(blank=True, null=True)

    objects = MemeTemplateQuerySet.as_manager()


class MemeInstance(models.Model):
    receiver = models.ForeignKey('bot.SlackUser', related_name='instances', on_delete=models.SET_NULL, null=True, blank=True)
    meme = models.ImageField(null=True, upload_to='meme_instances')
    template = models.ForeignKey('bot.MemeTemplate', related_name='instances', on_delete=models.CASCADE)
    included_cards = models.ManyToManyField('bot.TrelloCard', related_name='instances')
    date_created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_from_template(cls, user, template: MemeTemplate, cards: List[TrelloCard]):
        img = Image.open(template.template)
        for config in template.text_config:
            rendered_text = config['text'].format(**{
                card.list.name: card.name
                for card in cards
            })
            overlay_text(img, rendered_text, config['origin'], config['angle'], config['bounding_box'])

        instance = cls.objects.create(receiver=user, template=template)
        [instance.included_cards.add(card) for card in cards]

        buffer = BytesIO()
        img.save(fp=buffer, format='JPEG', quality=100)
        img_content = ContentFile(buffer.getvalue(), uuid.uuid4().hex)
        instance.meme = img_content
        instance.save()
        return instance
