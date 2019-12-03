import json

from django.conf import settings
from django.db import transaction

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class EventView(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        slack_message = request.data
        print(json.dumps(slack_message, indent=4))

        if slack_message.get('token') != settings.SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)
