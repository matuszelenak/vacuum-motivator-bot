from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def __str__(self):
        return f'{self.username} ({self.slack_user_id})'


class MemeTemplate(models.Model):
    template = models.ImageField(null=True, upload_to='memes')
    insert_text_x = models.IntegerField()
    insert_text_y = models.IntegerField()
