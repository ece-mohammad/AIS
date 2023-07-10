from http import client
from typing import *

from django.test import TestCase
from django.test.client import Client
from devices.models import Device
from test.pages.common import DeviceList

from test.utils.helpers import client_login, client_logout, create_member


FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="first_member",
    password="test_password",
)

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="second_member",
    password="test_password",
)

FIRST_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="first_device_group",
    description="first device group description",
)

SECOND_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="second_device_group",
    description="first device group description",
)

class TestDeviceList(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(**FIRST_MEMBER)
        self.second_member = create_member(**SECOND_MEMBER)
        
        self.first_device_group = self.first_member.devicegroup_set.create(**FIRST_DEVICE_GROUP)
        self.second_device_group = self.second_member.devicegroup_set.create(**SECOND_DEVICE_GROUP)
        
        self.first_device = self.first_device_group.device_set.create(
            name="first_device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_device_group.name}-first_device"),
            group=self.first_device_group,
        )
        
        client_login(self.client, FIRST_MEMBER)
        
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_device_list_member_with_no_devices(self):
        """Test that device list page shows a message when the member has no devices"""
        client_logout(self.client)
        client_login(self.client, SECOND_MEMBER)
        response = self.client.get(
            DeviceList.get_url(),
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You don't have any devices yet.")

    def test_device_list_shows_member_devices(self):
        response = self.client.get(
            DeviceList.get_url(),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_device.name)
        
    def test_device_list_does_not_show_inactive_devices(self):
        self.first_device.is_active = False
        self.first_device.save()
        
        response = self.client.get(
            DeviceList.get_url(),
            follow=True,
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You don't have any devices yet.")
