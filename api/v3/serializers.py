from rest_framework import serializers

from accounts.models import Member
from devices.models import Device, DeviceData, DeviceGroup
from django.utils import timezone


class MemberSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:member_details", lookup_url_kwarg="username", lookup_field="username")
    devicegroup_set = serializers.HyperlinkedRelatedField(view_name="api:group_details", lookup_url_kwarg="group_name", lookup_field="name", many=True, read_only=True)
    
    class Meta:
        model = Member
        fields = (
            "url",
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
            "devicegroup_set",
        )


class DeviceGroupSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:group_details", lookup_url_kwarg="group_name", lookup_field="name")
    creation_date = serializers.DateTimeField(default=timezone.now)
    owner = serializers.HyperlinkedRelatedField(view_name="api:member_details", lookup_url_kwarg="username", lookup_field="username", many=False, read_only=True)
    device_set = serializers.HyperlinkedRelatedField(view_name="api:device_details", lookup_url_kwarg="device_uid", lookup_field="uid", many=True, read_only=True)
    
    class Meta:
        model = DeviceGroup
        fields = (
            "url",
            "name",
            "id",
            "description",
            "creation_date",
            "owner",
            "device_set",
        )
    
    def validate_creation_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Creation date cannot be in the future.")
        return value


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:device_details", lookup_url_kwarg="device_uid", lookup_field="uid")
    group = serializers.HyperlinkedRelatedField(view_name="api:group_details", lookup_url_kwarg="group_name", lookup_field="name", many=False, read_only=True)
    
    class Meta:
        model = Device
        fields = (
            "url",
            "name",
            "uid",
            "date_added",
            "is_active",
            "group",
        )
    
    def validate_date_added(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Date added cannot be in the future.")
        return value


class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = (
            "id",
            "message",
            "date",
            "device_id",
        )
