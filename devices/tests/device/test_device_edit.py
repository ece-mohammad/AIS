from test.pages.common import DeviceCreate, DeviceDetails, DeviceEdit
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
    name="first device group",
    description="first device group",
)

SECOND_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="second device group",
    description="second device group",
)


class TestDeviceEdit(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(**FIRST_MEMBER)
        self.second_member = create_member(**SECOND_MEMBER)
        
        self.first_group = self.first_member.devicegroup_set.create(**FIRST_DEVICE_GROUP)
        self.second_group = self.first_member.devicegroup_set.create(**SECOND_DEVICE_GROUP)
        
        self.first_device = self.first_group.device_set.create(
            name="first device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-first device"),
            group=self.first_group,
        )
        
        client_login(self.client, FIRST_MEMBER)
        
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()

    def test_device_edit_name_required(self):
        """Test that the device name is required"""
        response = self.client.post(
            DeviceEdit.get_url(device_uid=self.first_device.uid),
            data=dict(
                name="", 
                group=self.first_device.group.pk
            ),
            follow=True,
        )
        
        form = response.context.get("form")
        self.assertFormError(form, "name", ["This field is required."])
        
    def test_device_edit_group_required(self):
        """Test that device group is required"""
        response = self.client.post(
            DeviceEdit.get_url(device_uid=self.first_device.uid),
            data=dict(
                name=self.first_device.name, 
            ),
            follow=True,
        )
        
        form = response.context.get("form")
        self.assertFormError(form, "group", ["This field is required."])
        
    def test_device_edit_changes_device_name(self):
        """Test that device edit page changes device name"""
        device_new_name = f"{self.first_device.name}_new"
        response = self.client.post(
            DeviceEdit.get_url(device_uid=self.first_device.uid),
            data=dict(
                name=device_new_name, 
                group=self.first_device.group.pk,
                is_active=True,
            ),
            follow=True,
        )
        self.first_device.refresh_from_db()
        
        self.assertRedirects(response, DeviceDetails.get_url(device_uid=self.first_device.uid), 302, 200, fetch_redirect_response=True)
        self.assertEqual(self.first_device.name, device_new_name)
        self.assertEqual(self.first_device.group, self.first_group)
        self.assertEqual(self.first_device.is_active, True)
        
    def test_device_edit_changes_device_group(self):
        """Test that device edit page changes device group"""
        response = self.client.post(
            DeviceEdit.get_url(device_uid=self.first_device.uid),
            data=dict(
                name=self.first_device.name, 
                group=self.second_group.pk,
                is_active=True,
            ),
            follow=True,
        )
        self.first_device.refresh_from_db()
        
        self.assertRedirects(response, DeviceDetails.get_url(device_uid=self.first_device.uid), 302, 200, fetch_redirect_response=True)
        self.assertEqual(self.first_device.name, self.first_device.name)
        self.assertEqual(self.first_device.group, self.second_group)
        self.assertEqual(self.first_device.is_active, True)
        
    def test_device_edit_no_changes(self):
        """Test that device edit page doesn't save if no changes were made"""
        response = self.client.get(
            DeviceEdit.get_url(device_uid=self.first_device.uid),
        )
        
        form_data = response.context.get("form").initial
        
        response = self.client.post(
            DeviceEdit.get_url(device_uid=self.first_device.uid),
            data=form_data,
            follow=True,
        )
        
        self.assertRedirects(response, DeviceDetails.get_url(device_uid=self.first_device.uid), 302, 200, fetch_redirect_response=True)
    
    def test_device_edit_another_member_device_404(self):
        """Test device edit returns 404 if device belongs to another member"""
        new_group = self.second_member.devicegroup_set.create(name="new device group")
        new_device = new_group.device_set.create(
            name="new device",
            uid=Device.generate_device_uid(f"{self.second_member.username}-{new_group.name}-new device"),
            group=new_group,
        )
        
        response = self.client.get(
            DeviceEdit.get_url(device_uid=new_device.uid),
        )
        
        self.assertEqual(response.status_code, 404)
