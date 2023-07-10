from test.pages.common import DeviceGroupDetails, LogIn
from test.utils.helpers import client_login, create_member
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

SECOND_DEVICE_GROUPS_DATA: Final[List[Dict[str, str]]] = [
    dict(name="test_group_1", description="second member test description 1",),
    dict(name="test_group_2", description="second member test description 2",),
    dict(name="test_group_5", description="second member test description 5",),
    dict(name="test_group_6", description="second member test description 6",),
]

class TestDeviceGroupDetails(TestCase):
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
        
        self.second_device_groups = DeviceGroup.objects.bulk_create(
        [
                DeviceGroup(
                    **group_data, 
                    owner=self.second_member
                ) for group_data in SECOND_DEVICE_GROUPS_DATA
            ],
            ignore_conflicts=True,
        )
        
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()

    def test_device_group_details_redirects_anon_user(self):
        client = Client()
        device_group_url = DeviceGroupDetails.get_url(group_name="test_group_1")
        response = client.get(
            device_group_url,
            follow=True,
        )
        next_url = f"{LogIn.get_url()}?next={device_group_url}"
        
        self.assertRedirects(response, next_url, 302, 200, fetch_redirect_response=True)
    
    def test_device_group_details_get_member_device_group(self):
        """Test device group details page shows device group details for the current device group"""
        device_group_url = DeviceGroupDetails.get_url(group_name="test_group_1")
        response = self.client.get(
            device_group_url,
            follow=True,
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, FIRST_DEVICE_GROUPS_DATA[0]["name"])
        self.assertContains(response, FIRST_DEVICE_GROUPS_DATA[0]["description"])
        
    def test_device_group_details_another_member_is_404(self):
        """Test device group details page returns 404 for another member's device group"""
        device_group_url = DeviceGroupDetails.get_url(group_name="test_group_5")
        response = self.client.get(
            device_group_url,
            follow=True,
        )
        response_html = response.content.decode(response.charset)
        
        self.assertEqual(response.status_code, 404)

