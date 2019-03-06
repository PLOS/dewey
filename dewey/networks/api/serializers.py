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

    def validate(self, data):
        host, network, address, canonical = data['host'], data['network'], data['address'], data['canonical']
        if canonical:
            assignments = AddressAssignment.objects.filter(host=host)
            canonical = set([assignment.canonical for assignment in assignments])
            if True in canonical:
                raise serializers.ValidationError(
                    'There is already a canonical assignment for {}'.format(host.hostname)
                )
        if address not in network.range:
            raise serializers.ValidationError('{} is not in the selected network'.format(address))
        if not AddressAssignment.objects.filter(network=network).filter(host=host).filter(address=address):
            if network.address_allocated(address):
                raise serializers.ValidationError('{} has already been allocated'.format(address))
        return data
