from test.pages.common import DeviceGroupList, LogIn
from test.utils.helpers import client_login, client_logout, create_member
from typing import *

from django.test import TestCase
from django.test.client import Client

from devices.models import DeviceGroup


FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="first_member",
    password="testpassword",
)

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="second_member",
    password="testpassword",
)

FIRST_DEVICE_GROUPS_DATA: Final[List[Dict[str, str]]] = [
    dict(name="test_group_1", description="first member test description 1",),
    dict(name="test_group_2", description="first member test description 2",),
    dict(name="test_group_3", description="first member test description 3",),
    dict(name="test_group_4", description="first member test description 4",),
]

class TestDeviceGroupList(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(
            **FIRST_MEMBER
        )
        
        self.second_member = create_member(
            **SECOND_MEMBER
        )
        
        client_login(self.client, FIRST_MEMBER)
        
        self.first_device_groups = DeviceGroup.objects.bulk_create(
            [
                DeviceGroup(
                    **group_data, 
                    owner=self.first_member
                ) for group_data in FIRST_DEVICE_GROUPS_DATA
            ],
            ignore_conflicts=True,
        )
        
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_device_group_list_redirects_anon_user(self):
        """Test that an anonymous user is redirected to the login page"""
        client = Client()
        response = client.get(
            DeviceGroupList.get_url(),
            follow=True,
        )
        next_url = f"{LogIn.get_url()}?next={DeviceGroupList.get_url()}"
        
        self.assertRedirects(response, next_url, 302, 200, fetch_redirect_response=True)

    def test_device_group_list_member_no_groups(self):
        """Test that a member with no device groups sees a (No device groups yet) message"""
        client_logout(self.client)
        client_login(self.client, SECOND_MEMBER)
        response = self.client.get(
            DeviceGroupList.get_url(),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You don't have any device groups yet.")

    def test_device_group_list_member_device_groups(self):
        """Test that a member with device groups sees all their device groups"""
        response = self.client.get(
            DeviceGroupList.get_url(),
        )

        page_device_groups = response.context.get("object_list")
        
        self.assertEqual(response.status_code, 200)
        for dev_group in self.first_device_groups:
            self.assertContains(response, dev_group.name)
        
        self.assertEqual(len(page_device_groups), len(self.first_device_groups))
        for (idx, dev_group) in enumerate(page_device_groups, start=0):
            self.assertEqual(dev_group.owner, self.first_member)
            self.assertEqual(dev_group.description, self.first_device_groups[idx].description)

    def test_device_group_display_device_count(self):
        """Test that device group list displays the number of devices in each group"""
        response = self.client.get(
            DeviceGroupList.get_url(),
        )
        
        self.assertEqual(response.status_code, 200)
        for dev_group in self.first_device_groups:
            dev_group = DeviceGroup.objects.get(name=dev_group.name, owner=self.first_member)
            device_count = dev_group.device_set.count()
            text = f"{device_count} device" if device_count == 1 else f"{device_count} devices"
            self.assertContains(response, f"({text})")
