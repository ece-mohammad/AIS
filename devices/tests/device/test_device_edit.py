from test.pages.common import DeviceDetails, DeviceEdit
from test.utils.helpers import client_login, create_member, page_in_response
from typing import *

from django.test import TestCase
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
    name="first_device_group",
    description="first device group",
)

SECOND_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="second_device_group",
    description="second device group",
)


class BaseDeviceEditTestCase(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(**FIRST_MEMBER)
        self.first_group = self.first_member.devicegroup_set.create(**FIRST_DEVICE_GROUP)
        self.first_device = self.first_group.device_set.create(
            name="first device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-first device"),
            group=self.first_group,
        )
        
        self.second_member = create_member(**SECOND_MEMBER)
        self.second_group = self.first_member.devicegroup_set.create(**SECOND_DEVICE_GROUP)
        self.second_device = self.second_group.device_set.create(
            name="second device",
            uid=Device.generate_device_uid(f"{self.second_member.username}-{self.second_group.name}-second device"),
            group=self.second_group,
        )
        
        client_login(self.client, FIRST_MEMBER)
        
        return super().setUp()


class testDeviceEditRendering(BaseDeviceEditTestCase):
    def test_device_edit_rendering(self):
        response = self.client.get(
            DeviceEdit.get_url(device_uid=self.first_device.uid),
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(page_in_response(DeviceEdit, response))


class TestDeviceEditForm(BaseDeviceEditTestCase):
    def setUp(self):
        ret = super().setUp()
        self.response = self.client.get(
            DeviceEdit.get_url(device_uid=self.first_device.uid),
            follow=True
        )
        self.form = self.response.context.get("form")
        self.name_filed = self.form.fields.get("name")
        self.group_field = self.form.fields.get("group")
        self.is_active_field = self.form.fields.get("is_active")
        return ret

    def test_device_edit_form_fields(self):
        self.assertTrue(self.response.status_code, 200)
        self.assertIsNotNone(self.form)
        self.assertEqual(len(self.form.fields), 3)
        self.assertIn("name", self.form.fields)
        self.assertIsNotNone(self.name_filed)
        self.assertIsNotNone(self.group_field)
        self.assertIsNotNone(self.is_active_field)

    def test_device_edit_form_fields_name(self):
        self.assertEqual(self.name_filed.label, "Device name")
        self.assertEqual(self.name_filed.required, True)
        self.assertEqual(self.name_filed.initial, None)
    
    def test_device_edit_form_fields_group(self):
        self.assertEqual(self.group_field.required, True)
        self.assertEqual(self.group_field.initial, None)
        self.assertQuerySetEqual(self.group_field.queryset, self.first_member.devicegroup_set.all(), ordered=False)

    def test_device_edit_form_fields_is_active(self):
        self.assertEqual(self.is_active_field.label, "Is device enabled")
        self.assertEqual(self.is_active_field.required, False)
        self.assertEqual(self.is_active_field.initial, True)


class TestDeviceEditView(BaseDeviceEditTestCase):
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
