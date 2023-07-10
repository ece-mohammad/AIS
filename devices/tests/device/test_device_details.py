from test.pages.common import DeviceDetails
from test.utils.helpers import client_login, create_member
from typing import *

from django.test import TestCase
from django.test.client import Client
from devices.models import Device


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

FIRST_DEVICE: Final[Dict[str, str]] = dict(
    name="first device",
)

SECOND_DEVICE: Final[Dict[str, str]] = dict(
    name="first device",
)

class TestDeviceDetails(TestCase):
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
            name=FIRST_DEVICE["name"],
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-{FIRST_DEVICE['name']}"),
            group=self.first_group,
        )
        
        self.second_device = self.second_group.device_set.create(
            name=FIRST_DEVICE["name"],
            uid=Device.generate_device_uid(f"{self.second_member.username}-{self.second_group.name}-{SECOND_DEVICE['name']}"),
            group=self.second_group,
        )
        
        client_login(self.client, FIRST_MEMBER)
        
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()

    def test_device_details_shows_device_data(self):
        """Test that device details page shows device details"""
        response = self.client.get(
            DeviceDetails.get_url(device_uid=self.first_device.uid),
            follow=True,
        )
        
        self.assertContains(response, self.first_device.name)
        self.assertContains(response, self.first_device.uid)
        self.assertContains(response, self.first_group.name)

    def test_device_details_another_member_device_404(self):
        """Test that device details page returns 404 for another member's device"""
        response = self.client.get(
            DeviceDetails.get_url(device_uid=self.second_device.uid),
            follow=True,
        )
        
        self.assertEqual(response.status_code, 404)

