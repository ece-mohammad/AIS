import json
from io import BytesIO
from typing import *

from django.contrib.auth.models import User
from django.forms import JSONField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.request import Request

from accounts.models import Member
from devices.models import Device, DeviceData, DeviceGroup


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def assert_value(obj, value, func=None, message="", *f_args, **f_kwargs):
    if func is None:
        func = lambda x: x

    if not func(obj, *f_args, **f_kwargs) == value:
        raise ValueError(message)


# -----------------------------------------------------------------------------
# MemberHyperLinkedFields
# -----------------------------------------------------------------------------
class MemberHyperlinkField:
    """
    Get member's URL
    """

    def assert_member_link_field(self, obj, view_name, lookup_field, lookup_url_kwarg):
        assert_value(
            obj=view_name,
            value="api:v1:member_details",
            message="view_name must be 'api:v1:member_details'.",
        )
        assert_value(
            obj=lookup_field,
            value="username",
            message="lookup_field must be 'username'.",
        )
        assert_value(
            obj=lookup_url_kwarg,
            value="username",
            message="lookup_url_kwarg must be 'username'.",
        )

        if not isinstance(obj, (Member, User)):
            raise ValueError("obj must be an instance of Member.")

    @classmethod
    def get_member_url_kwargs_from_request(cls, request):
        return dict(username=request.resolver_match.kwargs.get("username"))

    @classmethod
    def get_member_url_kwargs_from_instance(cls, member):
        return dict(username=member.username)

    @classmethod
    def get_member_url_kwargs(cls, instance, request):
        if isinstance(instance, (Member, User)):
            return MemberHyperlinkField.get_member_url_kwargs_from_instance(instance)
        return MemberHyperlinkField.get_member_url_kwargs_from_request(request)

    def get_url(self, obj, view_name, request, format):
        self.assert_member_link_field(
            obj=obj,
            view_name=view_name,
            lookup_field=self.lookup_field,
            lookup_url_kwarg=self.lookup_url_kwarg,
        )
        url_kwargs = self.get_member_url_kwargs(instance=obj, request=request)
        url = self.reverse(view_name, kwargs=url_kwargs, request=request, format=format)
        return url


class MemberHyperlinkedIdentityField(
    MemberHyperlinkField, serializers.HyperlinkedIdentityField
):
    """
    Get URL of current Member instance.
    """

    ...


class MemberHyperlinkedRelatedField(
    MemberHyperlinkField, serializers.HyperlinkedRelatedField
):
    """
    Get URL of related Member
    """

    ...


# -----------------------------------------------------------------------------
# DeviceGroupHyperLinkedFields
# -----------------------------------------------------------------------------
class DeviceGroupHyperlinkedField:
    """
    Get URL of current DeviceGroup instance
    """

    def assert_device_group_link_field(
        self, obj, view_name, lookup_field, lookup_url_kwarg
    ):
        assert_value(
            obj=view_name,
            value="api:v1:group_details",
            message="view_name must be 'api:v1:group_details'.",
        )
        assert_value(
            obj=lookup_field, value="name", message="lookup_field must be 'name'."
        )
        assert_value(
            obj=lookup_url_kwarg,
            value="group_name",
            message="lookup_url_kwarg must be 'group_name'.",
        )
        assert_value(
            obj=obj,
            value=DeviceGroup,
            func=type,
            message="obj must be an instance of DeviceGroup.",
        )

    @classmethod
    def get_device_group_url_kwargs_from_request(cls, request: Request):
        url_kwargs = MemberHyperlinkField.get_member_url_kwargs_from_request(request)
        url_kwargs.update(
            dict(group_name=request.resolver_match.kwargs.get("group_name"))
        )
        return url_kwargs

    @classmethod
    def get_device_group_url_kwargs_from_instance(cls, device_group: DeviceGroup):
        url_kwargs = MemberHyperlinkField.get_member_url_kwargs_from_instance(
            device_group.owner
        )
        url_kwargs.update(dict(group_name=device_group.name))
        return url_kwargs

    @classmethod
    def get_device_group_url_kwargs(cls, instance: DeviceGroup, request: Request):
        if isinstance(instance, DeviceGroup):
            return (
                DeviceGroupHyperlinkedField.get_device_group_url_kwargs_from_instance(
                    instance
                )
            )
        return DeviceGroupHyperlinkedField.get_device_group_url_kwargs_from_request(
            request
        )

    def get_url(self, obj, view_name, request, format):
        self.assert_device_group_link_field(
            obj=obj,
            view_name=view_name,
            lookup_field=self.lookup_field,
            lookup_url_kwarg=self.lookup_url_kwarg,
        )
        url_kwargs = DeviceGroupHyperlinkedField.get_device_group_url_kwargs(
            instance=obj, request=request
        )
        url = self.reverse(view_name, kwargs=url_kwargs, request=request, format=format)
        return url


class DeviceGroupHyperlinkedIdentityField(
    DeviceGroupHyperlinkedField, serializers.HyperlinkedIdentityField
):
    """
    Get URL of current DeviceGroup instance
    """

    ...


class DeviceGroupHyperlinkedRelatedField(
    DeviceGroupHyperlinkedField, serializers.HyperlinkedRelatedField
):
    """
    Get URL of related DeviceGroup
    """

    ...


# -----------------------------------------------------------------------------
# DeviceHyperLinkedFields
# -----------------------------------------------------------------------------
class DeviceHyperlinkedField:
    """
    Get URL of current Device instance.
    """

    def assert_device_link_field(self, obj, view_name, lookup_field, lookup_url_kwarg):
        assert_value(
            obj=view_name,
            value="api:v1:device_details",
            message="view_name must be 'api:v1:device_details'.",
        )
        assert_value(
            obj=lookup_field, value="uid", message="lookup_field must be 'uid'."
        )
        assert_value(
            obj=lookup_url_kwarg,
            value="device_uid",
            message="lookup_url_kwarg must be 'device_uid'.",
        )
        assert_value(
            obj=obj,
            value=Device,
            func=type,
            message="obj must be an instance of Device.",
        )

    @classmethod
    def get_device_url_kwargs_from_request(cls, request):
        url_kwargs = (
            DeviceGroupHyperlinkedField.get_device_group_url_kwargs_from_request(
                request
            )
        )
        url_kwargs.update(
            dict(device_uid=request.resolver_match.kwargs.get("device_uid"))
        )
        return url_kwargs

    @classmethod
    def get_device_url_kwargs_from_instance(cls, device):
        url_kwargs = (
            DeviceGroupHyperlinkedField.get_device_group_url_kwargs_from_instance(
                device.group
            )
        )
        url_kwargs.update(dict(device_uid=str(device.uid)))
        return url_kwargs

    @classmethod
    def get_device_url_kwargs(cls, instance, request):
        if isinstance(instance, Device):
            return DeviceHyperlinkedField.get_device_url_kwargs_from_instance(instance)
        return DeviceHyperlinkedField.get_device_url_kwargs_from_request(request)

    def get_url(self, obj, view_name, request, format):
        self.assert_device_link_field(
            obj=obj,
            view_name=view_name,
            lookup_field=self.lookup_field,
            lookup_url_kwarg=self.lookup_url_kwarg,
        )
        url_kwargs = DeviceHyperlinkedField.get_device_url_kwargs(
            instance=obj, request=request
        )
        url = self.reverse(view_name, kwargs=url_kwargs, request=request, format=format)
        return url


class DeviceHyperlinkedIdentityField(
    DeviceHyperlinkedField, serializers.HyperlinkedIdentityField
):
    """
    Get URL of current Device instance.
    """

    ...


class DeviceHyperlinkedRelatedField(
    DeviceHyperlinkedField, serializers.HyperlinkedRelatedField
):
    """
    Get URL of related Device
    """

    ...


# -----------------------------------------------------------------------------
# DeviceDataHyperLinkedFields
# -----------------------------------------------------------------------------
class DeviceDataHyperlinkedField:
    def assert_device_data_link_field(
        self, obj, view_name, lookup_field, lookup_url_kwarg
    ):
        assert_value(
            obj=view_name,
            value="api:v1:data_details",
            message="view_name must be 'api:v1:data_details'.",
        )
        assert_value(obj=lookup_field, value="id", message="lookup_field must be 'id'.")
        assert_value(
            obj=lookup_url_kwarg,
            value="data_id",
            message="lookup_url_kwarg must be 'data_id'.",
        )
        assert_value(
            obj=obj,
            value=DeviceData,
            func=type,
            message="obj must be an instance of DeviceData.",
        )

    @classmethod
    def get_device_data_url_kwargs_from_request(cls, request):
        url_kwargs = DeviceHyperlinkedField.get_device_url_kwargs_from_request(request)
        url_kwargs.update(dict(data_id=request.resolver_match.kwargs.get("data_id")))
        return url_kwargs

    @classmethod
    def get_device_data_url_kwargs_from_instance(cls, device_data):
        url_kwargs = DeviceHyperlinkedField.get_device_url_kwargs_from_instance(
            device_data.device
        )
        url_kwargs.update(dict(data_id=device_data.id))
        return url_kwargs

    @classmethod
    def get_device_data_url_kwargs(cls, instance, request):
        if isinstance(instance, DeviceData):
            return DeviceDataHyperlinkedField.get_device_data_url_kwargs_from_instance(
                instance
            )
        return DeviceDataHyperlinkedField.get_device_data_url_kwargs_from_request(
            request
        )

    def get_url(self, obj, view_name, request, format):
        self.assert_device_data_link_field(
            obj=obj,
            view_name=view_name,
            lookup_field=self.lookup_field,
            lookup_url_kwarg=self.lookup_url_kwarg,
        )
        url_kwargs = DeviceDataHyperlinkedField.get_device_data_url_kwargs(
            instance=obj, request=request
        )
        url = self.reverse(view_name, kwargs=url_kwargs, request=request, format=format)
        return url


class DeviceDataHyperlinkedIdentityField(
    DeviceDataHyperlinkedField, serializers.HyperlinkedIdentityField
):
    """
    Get URL of DeviceData instance.
    """

    ...


class DeviceDataHyperlinkedRelatedField(
    DeviceDataHyperlinkedField, serializers.HyperlinkedRelatedField
):
    """
    Get URL of related DeviceData
    """

    ...


# -----------------------------------------------------------------------------
# Serializer
# -----------------------------------------------------------------------------
class MemberSerializer(serializers.HyperlinkedModelSerializer):
    url = MemberHyperlinkedIdentityField(
        view_name="api:v1:member_details",
        lookup_url_kwarg="username",
        lookup_field="username",
    )
    devicegroup_set = DeviceGroupHyperlinkedRelatedField(
        view_name="api:v1:group_details",
        lookup_url_kwarg="group_name",
        lookup_field="name",
        many=True,
        read_only=True,
    )

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
            "devicegroup_set",
        )


class DeviceGroupSerializer(serializers.HyperlinkedModelSerializer):
    url = DeviceGroupHyperlinkedIdentityField(
        view_name="api:v1:group_details",
        lookup_url_kwarg="group_name",
        lookup_field="name",
    )
    creation_date = serializers.DateTimeField(default=timezone.now)
    owner = MemberHyperlinkedRelatedField(
        view_name="api:v1:member_details",
        lookup_url_kwarg="username",
        lookup_field="username",
        many=False,
        read_only=True,
    )
    device_set = DeviceHyperlinkedRelatedField(
        view_name="api:v1:device_details",
        lookup_url_kwarg="device_uid",
        lookup_field="uid",
        many=True,
        read_only=True,
    )
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

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
            raise serializers.ValidationError(
                "Field `creation_date` cannot be in the future."
            )
        return value


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    url = DeviceHyperlinkedIdentityField(
        view_name="api:v1:device_details",
        lookup_url_kwarg="device_uid",
        lookup_field="uid",
    )
    group = DeviceGroupHyperlinkedRelatedField(
        view_name="api:v1:group_details",
        lookup_url_kwarg="group_name",
        lookup_field="name",
        many=False,
        read_only=True,
    )
    devicedata_set = DeviceDataHyperlinkedRelatedField(
        view_name="api:v1:data_details",
        lookup_url_kwarg="data_id",
        lookup_field="id",
        many=True,
        read_only=True,
    )
    uid = serializers.UUIDField(format="hex_verbose", read_only=True)

    class Meta:
        model = Device
        fields = (
            "url",
            "name",
            "uid",
            "date_added",
            "is_active",
            "group",
            "devicedata_set",
        )

    def validate_date_added(self, value):
        if value > timezone.now():
            raise serializers.ValidationError(
                "Field `date_added` cannot be in the future."
            )
        return value

    def save(self, **kwargs):
        group: DeviceGroup = kwargs.get("group")
        user: Member = group.owner
        device_name = self.validated_data.get("name")
        device_uid = Device.generate_device_uid(
            f"{user.username}-{group.name}-{device_name}"
        )
        kwargs["uid"] = device_uid
        return super().save(**kwargs)


class DeviceDataSerializer(serializers.ModelSerializer):
    url = DeviceDataHyperlinkedIdentityField(
        view_name="api:v1:data_details", lookup_url_kwarg="data_id", lookup_field="id"
    )
    device = DeviceHyperlinkedRelatedField(
        view_name="api:v1:device_details",
        lookup_url_kwarg="device_uid",
        lookup_field="uid",
        many=False,
        read_only=True,
    )
    id = serializers.IntegerField(read_only=True, source="pk")
    message = JSONField()

    class Meta:
        model = DeviceData
        fields = (
            "url",
            "id",
            "message",
            "date",
            "device",
        )

    def validate_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value

    def validate_message(self, value):
        self.error_messages[
            "invalid_json"
        ] = "Message must be either a valid JSON object or a UTF-8 encoded JSON string."

        if isinstance(value, str):
            json_parser = JSONParser()

            try:
                stream = BytesIO(value.encode("utf-8"))
            except Exception as e:
                raise serializers.ValidationError(
                    self.error_messages["invalid_json"], code="invalid_json"
                )

            try:
                value = json_parser.parse(stream=stream)
            except Exception as e:
                raise serializers.ValidationError(
                    self.error_messages["invalid_json"], code="invalid_json"
                )

        elif isinstance(value, (dict, Mapping, list, Iterable)):
            try:
                json.dumps(value)
            except json.decoder.JSONDecodeError as e:
                raise serializers.ValidationError(
                    self.error_messages["invalid_json"], code="invalid_json"
                )

        else:
            raise serializers.ValidationError(
                self.error_messages["invalid_json"], code="invalid_json"
            )

        return value
