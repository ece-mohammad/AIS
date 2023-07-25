from test.pages.common import DeviceGroupCreate, DeviceGroupDetails, LogIn
from test.utils.helpers import (client_login, client_logout, create_member,
                                page_in_response)
from typing import *

from django.http import HttpResponse
from django.test import TestCase
from django.test.client import Client

from devices.models import DeviceGroup

FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="first_user",
    password="test_password",
)

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="second_user",
    password="test_password",
)

DEVICE_GROUP_DATA: Final[Dict[str, str]] = dict(
    name="test_group",
    description="test description",
)


class BaseDeviceGroupTestCase(TestCase):
    """Base test case form device group create tests, with common methods (setUp, tearDown, etc)"""
    def setUp(self) -> None:
        self.first_member = create_member(**FIRST_MEMBER)
        self.second_member = create_member(**SECOND_MEMBER)
        client_login(self.client, FIRST_MEMBER)
        
        super().setUp()


class TestDeviceGroupCreateRendering(BaseDeviceGroupTestCase):
    """Test device group create page rendering"""
    
    def test_device_group_create_template(self):
        """Test device group create page uses the correct template, view and title"""
        response = self.client.get(
            DeviceGroupCreate.get_url(),
            follow=True,
        )

        self.assertTrue(page_in_response(DeviceGroupCreate, response)[0])
        self.assertEqual(response.status_code, 200)


class TestDeviceGroupCreateForm(BaseDeviceGroupTestCase):
    """Test device group create form fields and form submission"""
    
    def test_device_group_create_form_field_name(self):
        """Test that the device group create form has a name field, unpopulated and is required"""
        # First we need to get the page for the form
        response = self.client.get(
            DeviceGroupCreate.get_url(),
            follow=True
        )

        # Then we need to get the form object
        form = response.context.get("form")

        # Then we can start checking the form fields
        self.assertEqual(len(form.fields), 2)
        
        self.assertIsNotNone(form.fields.get("description", None))
        self.assertEqual(form.fields["description"].label, "Device group description")
        self.assertEqual(form.fields["description"].required, False)
        self.assertEqual(form.fields["description"].initial, "")

    def test_device_group_create_form_field_description(self):
        """Test that the device group create form has a description field, unpopulated and is optional"""
        # First we need to get the page for the form
        response = self.client.get(
            DeviceGroupCreate.get_url(),
            follow=True
        )

        # Then we need to get the form object
        form = response.context.get("form")

        # Then we can start checking the form fields
        self.assertEqual(len(form.fields), 2)
        
        self.assertIsNotNone(form.fields.get("description", None))
        self.assertEqual(form.fields["description"].label, "Device group description")
        self.assertEqual(form.fields["description"].required, False)
        self.assertEqual(form.fields["description"].initial, "")

    def test_device_group_create_form_submit_name_is_required(self) -> None:
        """Test that the device group create form requires a name"""
        # Submit a POST request to the DeviceGroupCreate view with an empty name field
        response: HttpResponse = self.client.post(
            DeviceGroupCreate.get_url(),
            {"name": ""},
            follow=True,
        )
        
        # Assert that the form is invalid
        self.assertFormError(response.context.get("form"), "name", ["This field is required."])

    def test_device_group_create_form_submit_description_is_not_required(self) -> None:
        """Test that the device group create form does not require a description"""
        # Create a device group
        device_group_name = DEVICE_GROUP_DATA["name"]
        response: HttpResponse = self.client.post(
            DeviceGroupCreate.get_url(),
            {"name": device_group_name},
            follow=True,
        )
        
        form = response.context.get("form", None)
        group: DeviceGroup = DeviceGroup.objects.get(name=device_group_name)
        
        # Check that the form data is accepted (redirects to the device group details page)
        self.assertRedirects(response, DeviceGroupDetails.get_url(group_name="test_group"), 302, 200, fetch_redirect_response=True)
        
        # Check that the device group has been created
        self.assertEqual(DeviceGroup.objects.count(), 1)
        self.assertEqual(group.name, device_group_name)
        
        # Check that the default devices are associated with the group
        self.assertEqual(group.device_set.count(), 0)


class TestDeviceGroupCreate(BaseDeviceGroupTestCase):

    def test_device_group_create_redirects_anon_user(self):
        """Test device group create page redirects anonymous users to login page"""
        client = Client()
        response = client.get(
            DeviceGroupCreate.get_url(),
            follow=True,
        )
        next_url = f"{LogIn.get_url()}?next={DeviceGroupCreate.get_url()}"
        
        self.assertRedirects(response, next_url, 302, 200, fetch_redirect_response=True)

    def test_device_group_create_add_new_device_group(self):
        """Test device group create adds new device group to the current member"""
        self.assertEqual(DeviceGroup.objects.count(), 0)
        
        response = self.client.post(
            DeviceGroupCreate.get_url(),
            DEVICE_GROUP_DATA,
            follow=True,
        )
        device_group = DeviceGroup.objects.first()
        
        self.assertRedirects(response, DeviceGroupDetails.get_url(group_name=device_group.name), 302, 200, fetch_redirect_response=True)
        self.assertEqual(DeviceGroup.objects.count(), 1)
        self.assertEqual(device_group.name, DEVICE_GROUP_DATA["name"])
        self.assertEqual(device_group.description, DEVICE_GROUP_DATA["description"])
        self.assertEqual(device_group.owner, self.first_member)
        self.assertQuerySetEqual(self.first_member.devicegroup_set.all(), [device_group])
        
    def test_device_group_create_name_is_unique(self):
        """Test device group name field must be unique, creating multiple device groups with the same name (by the same member) is not allowed"""
        self.assertEqual(DeviceGroup.objects.count(), 0)
        
        response = self.client.post(
            DeviceGroupCreate.get_url(),
            DEVICE_GROUP_DATA,
            follow=True,
        )
        
        self.assertRedirects(response, DeviceGroupDetails.get_url(group_name=DEVICE_GROUP_DATA["name"]), 302, 200, fetch_redirect_response=True)
        self.assertEqual(DeviceGroup.objects.count(), 1)
        
        response = self.client.post(
            DeviceGroupCreate.get_url(),
            {"name": DEVICE_GROUP_DATA["name"]},
            follow=True,
        )
        
        self.assertFormError(response.context.get("form"), "name", ["A device group with this name already exists."])
        self.assertEqual(DeviceGroup.objects.count(), 1)
        self.assertEqual(self.first_member.devicegroup_set.count(), 1)

    def test_device_group_create_name_is_unique_per_user(self):
        """device name is unique for per user, creating multiple groups with the same name (by different members) is allowed"""
        self.assertEqual(DeviceGroup.objects.count(), 0)
        
        response = self.client.post(
            DeviceGroupCreate.get_url(),
            DEVICE_GROUP_DATA,
            follow=True,
        )
        
        self.assertRedirects(response, DeviceGroupDetails.get_url(group_name=DEVICE_GROUP_DATA["name"]), 302, 200, fetch_redirect_response=True)
        self.assertEqual(DeviceGroup.objects.count(), 1)
        
        client_logout(self.client)
        client_login(self.client, SECOND_MEMBER)
        response = self.client.post(
            DeviceGroupCreate.get_url(),
            DEVICE_GROUP_DATA,
            follow=True,
        )
        
        self.assertRedirects(response, DeviceGroupDetails.get_url(group_name=DEVICE_GROUP_DATA["name"]), 302, 200, fetch_redirect_response=True)
        self.assertEqual(DeviceGroup.objects.count(), 2)
        
        first_device_group = DeviceGroup.objects.first()
        second_device_group = DeviceGroup.objects.last()
        
        self.assertEqual(first_device_group.owner, self.first_member)
        self.assertEqual(second_device_group.owner, self.second_member)
        self.assertEqual(first_device_group.name, second_device_group.name)
