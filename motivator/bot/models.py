from django.conf import settings
from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models

from slack import WebClient


class SlackUserManager(UserManager):
    def for_user_id(self, user_id):
        try:
            return self.filter(slack_user_id=user_id).get()
        except SlackUser.DoesNotExist:
            client = WebClient(token=settings.SLACK_BOT_USER_TOKEN)
            user_info = client.users_info(user=user_id)['user']
            channel_id = client.im_open(user=user_id)['channel']['id']
            user = SlackUser.objects.create(
                slack_user_id=user_id,
                slack_channel_id=channel_id,
                username=user_info['name'],
                email=user_info['profile']['email'],
                first_name=user_info['profile'].get('first_name', ''),
                last_name=user_info['profile'].get('last_name', '')
            )
            user.set_unusable_password()
            user.save()
            return user


class SlackUser(AbstractUser):
    slack_user_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    slack_channel_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    objects = SlackUserManager()

    def __str__(self):
        return f'{self.username} ({self.slack_user_id})'
