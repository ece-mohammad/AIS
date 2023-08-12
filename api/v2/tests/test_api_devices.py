from test.utils.helpers import client_login, client_logout, create_member
from typing import *

from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from api.serializers import DeviceSerializer
from devices.models import Device, DeviceGroup


FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="test_user_1",
    password="test password",
)

FIRST_MEMBER_GROUPS: Final[List[DeviceGroup]] = [
    DeviceGroup(name="test_group_1", description="test group 1 description"),
    DeviceGroup(name="test_group_2", description="test group 2 description"),
]

FIRST_GROUP_DEVICES: Final[List[DeviceGroup]] = [
    Device(name="test_device_1"),
    Device(name="test_device_2"),
]

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="test_user_2",
    password="test password",
)

SECOND_MEMBER_GROUPS: Final[List[DeviceGroup]] = [
    DeviceGroup(name="test_group_3", description="test group 3 description"),
]

THIRD_GROUP_DEVICES: Final[List[DeviceGroup]] = [
    Device(name="test_device_3"),
]

# -----------------------------------------------------------------------------
# Base Test classes (common set ups)
# -----------------------------------------------------------------------------
class BaseDevicesAPIViewListTestCase(APITestCase):
    def setUp(self):
        self.url = reverse_lazy("api:devices_list")
        self.first_member = create_member(**FIRST_MEMBER)
        
        for group in FIRST_MEMBER_GROUPS:
            group.owner = self.first_member
            group.save()
        
        self.first_group = self.first_member.devicegroup_set.first()
        for dev in FIRST_GROUP_DEVICES:
            dev.uid = Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-{dev.name}")
            dev.group = self.first_group
            dev.save()
        
        self.second_member = create_member(**SECOND_MEMBER)
        
        for group in SECOND_MEMBER_GROUPS:
            group.owner = self.second_member
            group.save()
        
        self.third_group = self.second_member.devicegroup_set.first()
        for dev in THIRD_GROUP_DEVICES:
            dev.uid = Device.generate_device_uid(f"{self.second_member.username}-{self.third_group.name}-{dev.name}")
            dev.group = self.third_group
            dev.save()
        
        self.request = APIRequestFactory().get("/")
        self.request.user = self.first_member
        
        client_login(self.client, FIRST_MEMBER)


class BaseDevicesAPIViewDetailsTestCase(BaseDevicesAPIViewListTestCase):
    def setUp(self):
        ret = super().setUp()
        url = reverse_lazy("api:devices_list")
        request = APIRequestFactory().get(url)
        request.user = self.first_member
        self.device = DeviceSerializer(self.first_group.device_set.first(), context={"request": request})
        self.url = reverse_lazy(
            "api:device_details", 
            kwargs=dict(
                pk=Device.objects.filter(group__owner=self.first_member).first().id
            )
        )
        return ret


# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------
class TestDevicesAPISerializer(BaseDevicesAPIViewListTestCase):
    def setUp(self) -> None:
        ret = super().setUp()
        request_factory = APIRequestFactory()
        request_factory.default_format = "json"
        self.request = request_factory.get(self.url)
        self.request.user = self.first_member
        self.device_data = dict(
            name="test_device_group",
            description="test device group description",
            owner_id=self.first_member.id,
            creation_date=timezone.now(),
        )
        return ret
    
    def test_api_device_serializer_fields(self):
        serializer = DeviceSerializer()
        
        self.assertIsNotNone(serializer.fields.get("url"))
        self.assertIsNotNone(serializer.fields.get("name"))
        self.assertIsNotNone(serializer.fields.get("uid"))
        self.assertIsNotNone(serializer.fields.get("date_added"))
        self.assertIsNotNone(serializer.fields.get("is_active"))
        self.assertIsNotNone(serializer.fields.get("group"))
    
    def test_api_device_serializer_fields_name(self):
        serializer = DeviceSerializer()
        name_field = serializer.fields.get("name")
        self.assertTrue(name_field.required)
    
    def test_api_device_serializer_fields_uid(self):
        serializer = DeviceSerializer()
        uid_field = serializer.fields.get("uid")
        self.assertTrue(uid_field.required)
    
    def test_api_device_serializer_fields_date_added(self):
        serializer = DeviceSerializer()
        date_field = serializer.fields.get("date_added")
        self.assertFalse(date_field.required)
    
    def test_api_device_serializer_fields_is_active(self):
        serializer = DeviceSerializer()
        is_active = serializer.fields.get("is_active")
        self.assertFalse(is_active.required)
        
    def test_api_device_serializer_fields_group(self):
        serializer = DeviceSerializer()
        group_field = serializer.fields.get("group")
        self.assertTrue(group_field.read_only)


class TestDevicesAPIViewList(BaseDevicesAPIViewListTestCase):
    def test_api_device_list_anonymous_user(self):
        client_logout(self.client)
        response = self.client.get(
            self.url,
            follow=True,
        )
        error = response.data["detail"]
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(error, "Authentication credentials were not provided.")
        self.assertEqual(error.code, "not_authenticated")

    def test_api_device_list_get_devices(self):
        response = self.client.get(
            self.url, 
            data=dict(
                format="json"
            ),
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        for index, dev in enumerate(Device.objects.filter(group__owner=self.first_member).order_by("name"), start=0):
            self.assertEqual(response.data[index]["name"], dev.name)


class TestDevicesViewAPIDetails(BaseDevicesAPIViewDetailsTestCase):
    def test_api_device_details_get_device(self):
        response = self.client.get(
            self.url,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.device["name"].value)
        self.assertEqual(response.data["uid"], self.device["uid"].value)
        self.assertEqual(response.data["group"], self.device["group"].value)
        self.assertEqual(response.data["date_added"], self.device["date_added"].value)
        self.assertEqual(response.data["is_active"], self.device["is_active"].value)

    def test_api_device_details_non_existent_device_is_404(self):
        response = self.client.get(
            reverse_lazy("api:device_details", kwargs=dict(pk=999999)),
            follow=True,
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_device_details_non_another_member_device_is_404(self):
        client_logout(self.client)
        client_login(self.client, SECOND_MEMBER)
        
        response = self.client.get(
            self.url,
            follow=True
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
