from rest_framework import viewsets

from dewey.networks.api.serializers import NetworkSerializer
from dewey.networks.models import Network


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
