from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import IsAdminUser
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response

from dewey.networks.api.serializers import NetworkSerializer, AddressAssignmentSerializer
from dewey.networks.models import Network, AddressAssignment
from dewey.core.views import StandardApiMixin


class NetworkViewSet(StandardApiMixin, viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
    lookup_field = 'slug'
    lookup_value_regex = r'[\w\d-]+'


class AddressAssignmentViewSet(StandardApiMixin, viewsets.ModelViewSet):
    queryset = AddressAssignment.objects.all()
    serializer_class = AddressAssignmentSerializer


@api_view(['GET'])
@renderer_classes([renderers.JSONRenderer, renderers.BrowsableAPIRenderer])
@permission_classes([IsAdminUser])
def get_unused_address(request, slug):
    network = get_object_or_404(Network, slug=slug)
    return Response({'network': network.slug, 'address': network.get_unused_address()})


@api_view(['GET', 'HEAD'])
@renderer_classes([renderers.JSONRenderer, renderers.BrowsableAPIRenderer])
def api_root(request, fmt=None):
    return Response({
        'networks': reverse('api_v1:networks:networks-networks-list', request=request, format=fmt),
        'assignments': reverse('api_v1:networks:networks-assignments-list', request=request, format=fmt),
    })
