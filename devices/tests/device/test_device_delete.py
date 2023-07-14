from urllib import response
from test.pages.common import DeviceList, DeviceDelete, PasswordChange
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
    name="default device group",
    description="default device group for first member",
)

SECOND_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="default device group",
    description="default device group for second member",
)


class BaseDeviceDeleteTestCase(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(**FIRST_MEMBER)
        self.first_group = self.first_member.devicegroup_set.create(**FIRST_DEVICE_GROUP)
        self.first_device = self.first_group.device_set.create(
            name="first device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-first device"),
        )
        
        self.second_device = self.first_group.device_set.create(
            name="second device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{self.first_group.name}-second device"),
        )
        
        self.second_member = create_member(**SECOND_MEMBER)
        self.second_group = self.second_member.devicegroup_set.create(**SECOND_DEVICE_GROUP)
        self.third_device = self.second_group.device_set.create(
            name="third device",
            uid=Device.generate_device_uid(f"{self.second_member.username}-{self.first_group.name}-third device"),
        )
        
        client_login(self.client, FIRST_MEMBER)
        
        return super().setUp()


class TestDeviceDeleteRendering(BaseDeviceDeleteTestCase):
    def test_device_delete_template(self):
        """Test device delete template"""
        response = self.client.get(DeviceDelete.get_url(device_uid=self.first_device.uid))
        self.assertTrue(page_in_response(DeviceDelete, response)[0])


class TestDeviceDeleteForm(BaseDeviceDeleteTestCase):
    def setUp(self) -> None:
        ret = super().setUp()
        self.response = self.client.get(DeviceDelete.get_url(device_uid=self.first_device.uid))
        self.form = self.response.context.get("form")
        self.password_field = self.form.fields.get("password")
        return ret

    def test_device_delete_form_fields(self):
        self.assertEqual(len(self.form.fields), 1)
        self.assertIn("password", self.form.fields)
        self.assertIsNotNone(self.password_field)

    def test_device_delete_from_fields_password(self):
        self.assertEqual(self.password_field.label, "Password")
        self.assertEqual(self.password_field.required, True)
        self.assertEqual(self.password_field.initial, None)


class TestDeviceDeleteView(BaseDeviceDeleteTestCase):
    def test_device_delete_password_required(self):
        response = self.client.post(
            DeviceDelete.get_url(device_uid=self.first_device.uid),
            data=dict(),
            follow=True,
        )
        form = response.context.get("form")
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(form, "password", ["This field is required."])
        self.assertContains(response, "This field is required.")
    
    def test_device_delete_password_invalid(self):
        response = self.client.post(
            DeviceDelete.get_url(device_uid=self.first_device.uid),
            data=dict(
                password="invalid password",
            ),
            follow=True,
        )
        form = response.context.get("form")
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(form, "password", ["The password is incorrect"])
        self.assertContains(response, "The password is incorrect")
        self.assertTrue(Device.objects.filter(uid=self.first_device.uid).exists())
    
    def test_delete_device_remove_device(self) -> None:
        """Test device delete page removes device from database"""
        response = self.client.post(
            DeviceDelete.get_url(device_uid=self.first_device.uid),
            data=dict(
                password=FIRST_MEMBER["password"],
            ),
            follow=True
        )
        
        self.assertRedirects(response, DeviceList.get_url(), 302, 200, fetch_redirect_response=True)
        self.assertFalse(Device.objects.filter(uid=self.first_device.uid).exists())
    
    def test_delete_device_another_member_404(self):
        """Test delete device page returns 404 if device does not belong to current member"""
        response = self.client.post(
            DeviceDelete.get_url(device_uid=self.third_device.uid),
            data=dict(
                password=FIRST_MEMBER["password"],
            ),
            follow=True
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Device.objects.filter(uid=self.third_device.uid).exists())
