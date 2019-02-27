from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, renderers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

from dewey.salt.models import Change, Highstate, StateChange, StateError
from dewey.salt.api.serializers import ChangeSerializer, HighstateSerializer, StateChangeSerializer, StateErrorSerializer
from dewey.core.views import StandardApiMixin


class SaltApiPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        salt_group = get_object_or_404(Group, name='salt')
        if request.user.is_staff:
            return True
        if request.user.is_authenticated and request.method in permissions.SAFE_METHODS:
            return True
        return salt_group in request.user.groups.all()


class HighstateViewSet(StandardApiMixin, viewsets.ModelViewSet):
    permission_classes = (SaltApiPermission,)
    serializer_class = HighstateSerializer
    queryset = Highstate.objects.all()


class StateChangeViewSet(StandardApiMixin, viewsets.ModelViewSet):
    permission_classes = (SaltApiPermission,)
    serializer_class = StateChangeSerializer
    queryset = StateChange.objects.all()


class StateErrorViewSet(StandardApiMixin, viewsets.ModelViewSet):
    permission_classes = (SaltApiPermission,)
    serializer_class = StateErrorSerializer
    queryset = StateError.objects.all()


class ChangeViewSet(StandardApiMixin, viewsets.ModelViewSet):
    permission_classes = (SaltApiPermission,)
    serializer_class = ChangeSerializer
    queryset = Change.objects.all()


@api_view(['GET', 'HEAD'])
@renderer_classes([renderers.JSONRenderer, renderers.BrowsableAPIRenderer])
def api_root(request, fmt=None):
    return Response({
        'changes': reverse('api_v1:salt:salt-changes-list', request=request, format=fmt),
        'discovery': reverse('api_v1:salt-discovery', kwargs={'environment': 'dev'}, request=request, format=fmt),
        'highstates': reverse('api_v1:salt:salt-highstates-list', request=request, format=fmt),
        'hosts': reverse('api_v1:salt:salt-hosts-list', request=request, format=fmt),
        'secrets': reverse('api_v1:role-secrets', kwargs={'environment': 'dev', 'role': 'salt-master'}, request=request, format=fmt)
    })
