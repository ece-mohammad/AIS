from test.pages.common import DeviceDataList, LogIn
from test.utils.helpers import (
    client_login,
    client_logout,
    create_member,
    page_in_response,
)
from typing import *

from django.test import TestCase
from django.test.client import Client

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


class BaseDeviceDataListTestCase(TestCase):
    def setUp(self) -> None:
        ret = super().setUp()

        self.first_member = create_member(**FIRST_MEMBER)
        for group in FIRST_MEMBER_GROUPS:
            group.owner = self.first_member
            group.save()

        for index, device in enumerate(FIRST_MEMBER_DEVICES):
            device.group = FIRST_MEMBER_GROUPS[0 if index < 2 else 1]
            device.uid = Device.generate_device_uid(
                f"{self.first_member.username}-{device.group.name}-{device.name}"
            )
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
            device.uid = Device.generate_device_uid(
                f"{self.second_member.username}-{device.group.name}-{device.name}"
            )
            device.save()

        client_login(self.client, FIRST_MEMBER)

        return ret


class TestDeviceDataListRendering(BaseDeviceDataListTestCase):
    def setUp(self) -> None:
        ret = super().setUp()
        self.response = self.client.get(
            DeviceDataList.get_url(),
            follow=True,
        )
        return ret

    def test_device_data_list_rendering(self) -> None:
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(page_in_response(DeviceDataList, self.response)[0])


class TestDeviceDataListView(BaseDeviceDataListTestCase):
    def test_device_data_list_redirects_anonymous_user(self):
        client = Client()
        response = client.get(
            DeviceDataList.get_url(),
            follow=True,
        )
        next_url = f"{LogIn.get_url()}?next={DeviceDataList.get_url()}"
        self.assertRedirects(response, next_url)

    def test_device_data_list_shows_all_member_device_data(self):
        response = self.client.get(
            DeviceDataList.get_url(),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        for message in FIRST_DEVICE_DATA:
            self.assertContains(response, message.message)

    def test_device_data_list_shows_message_when_no_data(self):
        client_logout(self.client)
        client_login(self.client, SECOND_MEMBER)
        response = self.client.get(
            DeviceDataList.get_url(),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No data available yet")

    def test_device_data_list_shows_only_members_device_data(self):
        client_logout(self.client)
        client_login(self.client, SECOND_MEMBER)
        response = self.client.get(
            DeviceDataList.get_url(),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        for message in FIRST_DEVICE_DATA:
            self.assertNotContains(response, message.message)

    def test_device_data_list_pagination(self):
        extra_data = DeviceData.objects.bulk_create(
            [
                DeviceData(
                    message=f"extra_message_{index}",
                    device=Device.objects.filter(
                        group__owner=self.first_member
                    ).first(),
                )
                for index in range(11, 31)
            ],
        )

        page_1 = self.client.get(
            f"{DeviceDataList.get_url()}?page=1",
            follow=True,
        )

        page_2 = self.client.get(
            f"{DeviceDataList.get_url()}?page=2",
            follow=True,
        )

        page_3 = self.client.get(
            f"{DeviceDataList.get_url()}?page=3",
            follow=True,
        )

        self.assertEqual(page_1.status_code, 200)
        for message in FIRST_DEVICE_DATA:
            self.assertContains(page_1, message.message)

        self.assertEqual(page_2.status_code, 200)
        for message in extra_data[:10]:
            self.assertContains(page_2, message.message)

        self.assertEqual(page_3.status_code, 200)
        for message in extra_data[10:]:
            self.assertContains(page_3, message.message)
