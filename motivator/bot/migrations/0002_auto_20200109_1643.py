# Generated by Django 3.0 on 2020-01-09 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='memetemplate',
            name='action_types',
        ),
        migrations.AddField(
            model_name='memeinstance',
            name='receiver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='instances', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='memetemplate',
            name='required_lists',
            field=models.ManyToManyField(related_name='template', to='bot.TrelloList'),
        ),
    ]
