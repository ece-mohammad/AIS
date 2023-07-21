from test.pages.common import DeviceDataDetails, LogIn
from test.utils.helpers import client_login, create_member, page_in_response
from typing import *

from django.test.client import Client
from django.test import TestCase
from django.db.models import Count

from accounts.models import Member
from devices.models import Device, DeviceData, DeviceGroup


FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="first_member",
    password="test_password",
)

FIRST_MEMBER_GROUPS: Final[List[DeviceGroup]] = [
    DeviceGroup(name="first_member_group_1"),
    DeviceGroup(name="first_member_group_2"),
]

FIRST_MEMBER_DEVICES: Final[List[DeviceGroup]] = [
    Device(name="first_member_device_1"),
    Device(name="first_member_device_2"),
    Device(name="first_member_device_3"),
    Device(name="first_member_device_4"),
]

FIRST_DEVICE_DATA: Final[List[Dict[str, str]]] = [
    DeviceData(message="test_message_01"),
    DeviceData(message="test_message_02"),
    DeviceData(message="test_message_03"),
    DeviceData(message="test_message_04"),
    DeviceData(message="test_message_05"),
    DeviceData(message="test_message_06"),
    DeviceData(message="test_message_07"),
    DeviceData(message="test_message_08"),
    DeviceData(message="test_message_09"),
    DeviceData(message="test_message_10"),
]

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="second_member",
    password="test_password",
)

SECOND_MEMBER_GROUPS: Final[List[DeviceGroup]] = [
    DeviceGroup(name="second_member_group_1"),
    DeviceGroup(name="second_member_group_2"),
]

SECOND_MEMBER_DEVICES: Final[List[DeviceGroup]] = [
    Device(name="second_member_device_1"),
    Device(name="second_member_device_2"),
    Device(name="second_member_device_3"),
    Device(name="second_member_device_4"),
]

class BaseDeviceDataDetailsTestCase(TestCase):
    """Base test case for device data details views"""
    
    def setUp(self) -> None:
        ret = super().setUp()
        
        self.first_member = create_member(**FIRST_MEMBER)
        for group in FIRST_MEMBER_GROUPS:
            group.owner = self.first_member
            group.save()
            
        for index, device in enumerate(FIRST_MEMBER_DEVICES):
            device.group = FIRST_MEMBER_GROUPS[0 if index < 2 else 1]
            device.uid = Device.generate_device_uid(f"{self.first_member.username}-{device.group.name}-{device.name}")
            device.save()
        
        first_device = Device.objects.first()
        for index, data in enumerate(FIRST_DEVICE_DATA):
            data.device = first_device
            data.save()
        
        self.second_member = create_member(**SECOND_MEMBER)
        for group in SECOND_MEMBER_GROUPS:
            group.owner = self.second_member
            group.save()
        
        for index, device in enumerate(SECOND_MEMBER_DEVICES):
            device.group = SECOND_MEMBER_GROUPS[0 if index < 2 else 1]
            device.uid = Device.generate_device_uid(f"{self.second_member.username}-{device.group.name}-{device.name}")
            device.save()

        client_login(self.client, FIRST_MEMBER)
        
        return ret


class TestDeviceDataRendering(BaseDeviceDataDetailsTestCase):
    """Test device data rendering"""
    def setUp(self) -> None:
        ret = super().setUp()
        self.response = self.client.get(
            DeviceDataDetails.get_url(data_id=1),
            follow=True,
        )
        return ret
    
    def test_base_device_data_setup(self):
        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(DeviceGroup.objects.count(), 4)
        self.assertEqual(Device.objects.count(), 8)

        self.assertQuerysetEqual(self.first_member.username, FIRST_MEMBER["username"])
        self.assertEqual(self.first_member.devicegroup_set.count(), len(FIRST_MEMBER_GROUPS))
        self.assertEqual(self.first_member.devicegroup_set.first().name, FIRST_MEMBER_GROUPS[0].name)
        self.assertEqual(self.first_member.devicegroup_set.last().name, FIRST_MEMBER_GROUPS[1].name)
        self.assertEqual(self.first_member.devicegroup_set.first().device_set.count(), len(FIRST_MEMBER_DEVICES) // 2)
        self.assertEqual(self.first_member.devicegroup_set.last().device_set.count(), len(FIRST_MEMBER_DEVICES) // 2)
        self.assertDictContainsSubset(
            dict(device_count=4), 
            Member.objects.filter(pk=self.first_member.pk).annotate(device_count=Count("devicegroup__device", unique=True)).values()[0]
        )
        self.assertEqual(DeviceData.objects.count(), len(FIRST_DEVICE_DATA))
        self.assertEqual(Device.objects.first().devicedata_set.count(), len(FIRST_DEVICE_DATA))

    def test_device_data_details_rendering(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(page_in_response(DeviceDataDetails, self.response)[0])


class TestDeviceDataDetailsView(BaseDeviceDataDetailsTestCase):
    """Test device data details view"""
    
    def test_device_data_details_redirects_anonymous_user(self):
        client = Client()
        response = client.get(
            DeviceDataDetails.get_url(data_id=1),
            follow=True
        )
        next_url = f"{LogIn.get_url()}?next={DeviceDataDetails.get_url(data_id=1)}"
        self.assertRedirects(response, next_url, 302, 200, fetch_redirect_response=True)
    
    def test_device_data_details_shows_data_message(self):
        response = self.client.get(
            DeviceDataDetails.get_url(data_id=1),
            follow=True
        )
        self.assertContains(response, FIRST_DEVICE_DATA[0].message)
        self.assertContains(response, FIRST_MEMBER_DEVICES[0].name)
    
    def test_device_data_details_another_member_device_is_404(self):
        client = Client()
        client_login(client, SECOND_MEMBER)
        response = client.get(
            DeviceDataDetails.get_url(data_id=1),
            follow=True
        )
        self.assertEqual(response.status_code, 404)
