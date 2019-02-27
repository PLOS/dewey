from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers as serializers

from dewey.environments import OperatingSystem
from dewey.environments.models import Cluster, Host, Environment, Role


class ClusterSerializer(serializers.ModelSerializer):
    kind = serializers.SerializerMethodField()
    members = serializers.SlugRelatedField(slug_field='hostname', queryset=Host.objects.all(), many=True)

    class Meta:
        model = Cluster
        fields = ('id', 'name', 'description', 'kind', 'members')

    def get_kind(self, obj):
        return obj.get_kind_display()


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = ('id', 'name', 'hostname_regex', 'description', 'monitored')


class OperatingSystemField(serializers.Field):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        return OperatingSystem.__members__.get(data)


class HostSerializer(serializers.ModelSerializer):
    environment = serializers.SlugRelatedField(slug_field='name', queryset=Environment.objects.all())
    parent_type = serializers.SlugRelatedField(slug_field='model', queryset=ContentType.objects.all())
    roles = serializers.SlugRelatedField(slug_field='name', queryset=Role.objects.all(), many=True)
    operating_system = OperatingSystemField()

    class Meta:
        model = Host
        fields = ('id', 'hostname', 'environment', 'roles', 'operating_system', 'parent_type', 'parent_id')


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'description')


class SaltHostSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    environment = serializers.SerializerMethodField()

    class Meta:
        # TODO: remove environment and roles fields
        # after salt is transitioned to using grains field
        model = Host
        fields = ('id', 'hostname', 'ip_addresses', 'environment', 'roles', 'grains')

    def get_roles(self, obj):
        return [role.name for role in obj.roles.all()]

    def get_environment(self, obj):
        return obj.environment.name


class SaltHostSecretsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ('id', 'hostname', 'salt_secrets')

