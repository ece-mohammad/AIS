from test.pages.common import DeviceCreate, DeviceList, DeviceDelete
from test.utils.helpers import client_login, create_member
from typing import *

from django.test import TestCase
from django.test.client import Client
from django.db.models import Count
from devices.models import DeviceGroup, Device


FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="first_member",
    password="testpassword",
)

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="second_member",
    password="testpassword",
)

FIRST_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="default device group",
    description="default device group for first member",
)

SECOND_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="default device group",
    description="default device group for second member",
)


class TestDeviceDelete(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(
            **FIRST_MEMBER
        )
        self.second_member = create_member(
            **SECOND_MEMBER
        )
        
        self.first_group = self.first_member.devicegroup_set.create(**FIRST_DEVICE_GROUP)
        self.second_group = self.second_member.devicegroup_set.create(**SECOND_DEVICE_GROUP)
        
        self.first_device = self.first_group.device_set.create(
            name="first device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-first device"),
        )
        
        self.second_device = self.first_group.device_set.create(
            name="second device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-second device"),
        )
        
        self.third_device = self.second_group.device_set.create(
            name="third device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-third device"),
        )
        
        client_login(self.client, FIRST_MEMBER)
        
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()

    def test_delete_device_view(self) -> None:
        """Test device delete page removes device from database"""
        response = self.client.post(
            DeviceDelete.get_url(device_uid=self.first_device.uid),
            follow=True
        )
        
        self.assertRedirects(response, DeviceList.get_url(), 302, 200, fetch_redirect_response=True)
        self.assertFalse(Device.objects.filter(uid=self.first_device.uid).exists())
    
    def test_delete_device_another_member_404(self):
        """Test delete device page returns 404 if device does not belong to current member"""
        response = self.client.post(
            DeviceDelete.get_url(device_uid=self.third_device.uid),
            follow=True
        )
        
        self.assertEqual(response.status_code, 404)
