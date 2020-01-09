import ast

from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView

from bot.models import SlackUser, MemeTemplate, TrelloCard
from bot.slack import client
from bot.trello import trello_api_request


class SlackUserCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        slack_users = client.users_list()['members']
        slack_choices = [(user['id'], user['name']) for user in filter(lambda x: x.get('deleted', False) is not True, slack_users)]

        trello_users = trello_api_request(f'boards/{settings.TRELLO_BOARD_ID}/members', {})
        trello_choices = [(user['id'], user['fullName']) for user in trello_users]

        self.fields['slack_user_id'] = forms.ChoiceField(widget=forms.Select, choices=slack_choices)
        self.fields['trello_id'] = forms.ChoiceField(widget=forms.Select, choices=trello_choices)

    class Meta:
        model = SlackUser
        fields = '__all__'


@admin.register(SlackUser)
class SlackUserAdmin(admin.ModelAdmin):
    form = SlackUserCreateForm


class MemeTemplateTextAddForm(forms.Form):
    bound_box = forms.CharField()
    origin = forms.CharField()
    angle = forms.FloatField()
    text = forms.CharField()


class MemeTemplateTextAddView(FormView):
    template_name = 'admin/template_add_text.html'
    form_class = MemeTemplateTextAddForm

    def dispatch(self, request, *args, **kwargs):
        try:
            self.meme_template = MemeTemplate.objects.get(pk=kwargs.get('pk'))
        except MemeTemplate.DoesNotExist:
            return HttpResponseRedirect(reverse('admin:bot_memetemplate_change_list'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['image_path'] = self.meme_template.template.url
        data['template'] = self.meme_template
        return data

    @transaction.atomic
    def form_valid(self, form):
        self.meme_template.text_config = self.meme_template.text_config or []
        self.meme_template.text_config.append(
            {
                'bounding_box': ast.literal_eval(form.cleaned_data['bound_box']),
                'origin': ast.literal_eval(form.cleaned_data['origin']),
                'angle': form.cleaned_data['angle'],
                'text': form.cleaned_data['text']
            }
        )
        self.meme_template.save()
        return HttpResponseRedirect(reverse('admin:meme_template_add_text', kwargs={'pk': self.meme_template.pk}))


@admin.register(MemeTemplate)
class MemeTemplateAdmin(admin.ModelAdmin):
    def get_urls(self):
        return [
            *super().get_urls(),
            url(r'^(?P<pk>\d+)/add-text$', self.admin_site.admin_view(MemeTemplateTextAddView.as_view()), name='meme_template_add_text'),
        ]


@admin.register(TrelloCard)
class TrelloCardAdmin(admin.ModelAdmin):
    list_display = ['trello_id', 'name']
