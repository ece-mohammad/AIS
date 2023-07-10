from test.pages.common import DeviceCreate, DeviceDetails
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


class TestDeviceCreateView(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(
            **FIRST_MEMBER
        )

        self.second_member = create_member(
            **SECOND_MEMBER
        )
        
        client_login(self.client, FIRST_MEMBER)
        
        self.first_member.devicegroup_set.create(**FIRST_DEVICE_GROUP)
        self.second_member.devicegroup_set.create(**SECOND_DEVICE_GROUP)
        
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()

    def test_create_device_adds_device_to_group_and_member(self):
        """Test creating a new device, and that it was added to the group and member"""
        response = self.client.post(
            DeviceCreate.get_url(),
            data=dict(
                name="test device",
                group=DeviceGroup.objects.get(name=FIRST_DEVICE_GROUP["name"], owner=self.first_member).pk,
            ),
            follow=True,
        )
        device_group = self.first_member.devicegroup_set.all().annotate(
            device_count=Count("device"),
        ).first()
        
        device = device_group.device_set.first()
        self.assertRedirects(response, DeviceDetails.get_url(device_uid=device.uid), 302, 200, fetch_redirect_response=True)
        self.assertEqual(device_group.name, FIRST_DEVICE_GROUP["name"])
        self.assertEqual(device_group.device_set.count(), 1)
        self.assertEqual(device.name, "test device")

    def test_create_device_unique_name(self):
        """Test creating a new device with a the same name as an existing device, for the same member, is not allowed"""
        device_group = self.first_member.devicegroup_set.first()
        device_data = dict(
            name="test device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{device_group.name}-test device"),
            group=device_group,
        )
        device_group.device_set.create(**device_data)

        response = self.client.post(
            DeviceCreate.get_url(),
            data=dict(
                name=device_data["name"],
                group=device_group.pk,
            ),
            follow=True,
        )
        
        form = response.context.get("form")
        self.assertFormError(form, "name", ["A device with this name already exists."])
        self.assertInHTML("A device with this name already exists.", response.content.decode(response.charset))

    def test_create_device_same_name_different_group(self):
        """Test creating a new device with a the same name as an existing device, in the same device group (owned by the same member), is not allowed"""
        device_group = self.first_member.devicegroup_set.first()
        device_data = dict(
            name="test device",
            uid=Device.generate_device_uid(f"{self.first_member.username}-{device_group.name}-test device"),
            group=device_group,
        )
        device = device_group.device_set.create(**device_data)
        new_device_group = self.first_member.devicegroup_set.create(
            name="new device group",
            description="new device group for first member",
            owner=self.first_member,
        )
        
        response = self.client.post(
            DeviceCreate.get_url(),
            data=dict(
                name=device.name,
                group=new_device_group.pk,
            ),
            follow=True,
        )
        
        form = response.context.get("form")
        self.assertFormError(form, "name", ["A device with this name already exists."])
    
    def test_create_device_same_name_different_member(self):
        """Test creating a new device with the same name, for different members is allowed. The created devices are added to members' device groups"""
        device_group = self.second_member.devicegroup_set.first()
        device_data = dict(
            name="test device",
            uid=Device.generate_device_uid(f"{self.second_member.username}-{device_group.name}-test device"),
            group=device_group,
        )
        device = device_group.device_set.create(**device_data)

        response = self.client.post(
            DeviceCreate.get_url(),
            data=dict(
                name=device.name,
                group=self.first_member.devicegroup_set.first().pk,
            ),
            follow=True,
        )
        
        new_device = self.first_member.devicegroup_set.first().device_set.first()
        self.assertRedirects(response, DeviceDetails.get_url(device_uid=new_device.uid), 302, 200, fetch_redirect_response=True)
        self.assertEqual(self.first_member.devicegroup_set.first().device_set.count(), 1)
        self.assertEqual(self.second_member.devicegroup_set.first().device_set.count(), 1)
        self.assertEqual(self.first_member.devicegroup_set.first().device_set.first().name, device.name)
