from getpass import getpass
from requests.auth import HTTPBasicAuth
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from hardware.models import Server



class Command(BaseCommand):
    def _get_field(self, name, fields):
        for field in fields:
            if field['title'] == name:
                return field['values']

    def _get_auth(self):
        if settings.JIRA_USERNAME == '':
            jira_user = input('Jira Username: ')
        else:
            jira_user = settings.JIRA_USERNAME
        if settings.JIRA_PASSWORD == '':
           jira_password = getpass('Jira Password: ')
        else:
            jira_password = settings.JIRA_PASSWORD
        return HTTPBasicAuth(jira_user, jira_password)

    def handle(self, *args, **options):
        url = '/'.join([settings.JIRA_URL, 'rest', 'com-spartez-ephor', '1.0', 'search'])
        auth = self._get_auth()
        payload = {'query': 'Category=Servers'}
        request = requests.get(url, auth=auth, params=payload)
        request.raise_for_status()
        assets = [item for item in request.json()['items'] if item['typeName'] == 'Computer']
        for asset in assets:
            status = self._get_field('Asset Status', asset['fields'])
            if status[0] == 'Deployed':
              try:
                  server = Server.objects.get(ephor_id=asset['id'])
              except Server.DoesNotExist:
                  server = Server(ephor_id=asset['id'])
              server.asset_tag = self._get_field('Title', asset['fields'])[0]
              server.manufacturer = self._get_field('Manufacturer', asset['fields'])[0]
              server.model = self._get_field('Model', asset['fields'])[0]
              server.serial = self._get_field('Serial Number', asset['fields'])[0]
              server.save()
