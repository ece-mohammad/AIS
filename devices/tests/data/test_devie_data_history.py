from datetime import timedelta
from test.pages.common import DeviceDataHistory
from test.utils.helpers import client_login, create_member, page_in_response
from typing import *

from django.conf import settings
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

DATA_HISTORY_PAGE_COUNT: Final[int] = settings.PAGINATION_SIZE


class BaseDeviceDataHistoryTestCase(TestCase):
    """Base test case for device data details views"""

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

        self.first_device = Device.objects.filter(
            group__owner=self.first_member
        ).first()
        for index, data in enumerate(FIRST_DEVICE_DATA):
            data.device = self.first_device
            data.date += timedelta(minutes=index + 1)
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

        self.second_device = Device.objects.filter(
            group__owner=self.second_member
        ).first()

        client_login(self.client, FIRST_MEMBER)

        return ret


class TestDeviceDataHistoryView(BaseDeviceDataHistoryTestCase):
    def test_device_data_history_rendering(self):
        response = self.client.get(
            DeviceDataHistory.get_url(device_uid=self.first_device.uid),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(page_in_response(DeviceDataHistory, response)[0])

    def test_device_data_history_show_device_data(self):
        response = self.client.get(
            DeviceDataHistory.get_url(device_uid=self.first_device.uid),
            follow=True,
        )
        data_count = min(len(FIRST_DEVICE_DATA), DATA_HISTORY_PAGE_COUNT)
        self.assertEqual(response.status_code, 200)
        for data in FIRST_DEVICE_DATA[::-1][:data_count]:
            self.assertContains(response, data.message)
            self.assertContains(response, data.date.strftime("%Y/%m/%d, %H:%M:%S"))

    def test_device_data_history_show_message_when_no_data(self):
        client = Client()
        client_login(client, SECOND_MEMBER)
        response = client.get(
            DeviceDataHistory.get_url(device_uid=self.second_device.uid),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The device has not sent any data yet.")

    def test_device_data_history_pagination(self):
        DeviceData.objects.bulk_create(
            [
                DeviceData(
                    device=self.first_device,
                    message=f"test_message_{index}",
                    date=FIRST_DEVICE_DATA[0].date + timedelta(minutes=index),
                )
                for index in range(11, DATA_HISTORY_PAGE_COUNT + 1)
            ]
        )

        device_data = DeviceData.objects.filter(device=self.first_device).order_by(
            "-date"
        )
        history_page_count = (len(device_data) // DATA_HISTORY_PAGE_COUNT) + 1

        for page_index in range(history_page_count):
            page_data = device_data[
                page_index
                * DATA_HISTORY_PAGE_COUNT : (page_index + 1)
                * DATA_HISTORY_PAGE_COUNT
            ]
            response = self.client.get(
                DeviceDataHistory.get_url(
                    device_uid=self.first_device.uid, page=page_index + 1
                ),
                follow=True,
            )

            self.assertEqual(response.status_code, 200)
            for data in page_data:
                self.assertContains(response, data.message)
                self.assertContains(response, data.date.strftime("%Y/%m/%d, %H:%M:%S"))

    def test_device_data_history_invalid_uid_is_404(self):
        response = self.client.get(
            DeviceDataHistory.get_url(device_uid=self.second_device.uid),
            follow=True,
        )

        self.assertEqual(response.status_code, 404)
