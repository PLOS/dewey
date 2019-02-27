from rest_framework import serializers

from dewey.environments.models import Host
from dewey.networks.models import Network, AddressAssignment


class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ('slug', 'description', 'interface_id', 'cidr', 'mask_bits', 'netmask', 'reverse_zone')


class AddressAssignmentSerializer(serializers.ModelSerializer):
    host = serializers.SlugRelatedField(slug_field='hostname', queryset=Host.objects.all())
    network = serializers.SlugRelatedField(slug_field='slug', queryset=Network.objects.all())

    class Meta:
        model = AddressAssignment
        fields = ('id', 'host', 'address', 'network', 'canonical')