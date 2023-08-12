from datetime import timedelta
from test.pages.common import DeviceDetails
from test.utils.helpers import client_login, create_member
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

MOST_RECENT_COUNT: Final[int] = settings.MOST_RECENT_SIZE


class BaseDeviceDataInDeviceDetailsTestCase(TestCase):
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


class TestDeviceDetailsViewWithDeviceData(BaseDeviceDataInDeviceDetailsTestCase):
    """
    Test that device data view shows:
        - last 10 device data messages for a device
        - last update data (last message date)
    """

    def setUp(self) -> None:
        ret = super().setUp()
        self.second_client = Client()
        client_login(self.second_client, SECOND_MEMBER)
        return ret

    def test_device_details_show_last_device_data_date(self):
        response = self.client.get(
            DeviceDetails.get_url(device_uid=self.first_device.uid),
            follow=True,
        )
        most_recent_message_date = (
            self.first_device.devicedata_set.filter().order_by("-date").first().date
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(most_recent_message_date, response.context_data["last_update"])
        self.assertContains(
            response, most_recent_message_date.strftime(r"%Y/%m/%d, %H:%M:%S")
        )

    def test_device_details_show_most_recent_device_data_messages(self):
        response = self.client.get(
            DeviceDetails.get_url(device_uid=self.first_device.uid),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        for device_data in self.first_device.devicedata_set.all().order_by("-date")[
            :MOST_RECENT_COUNT
        ]:
            self.assertContains(response, device_data.message)

    def test_device_details_show_preset_message_when_no_data(self):
        response = self.second_client.get(
            DeviceDetails.get_url(device_uid=self.second_device.uid),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No data")

    def test_device_details_show_blank_last_update_when_no_message(self):
        response = self.second_client.get(
            DeviceDetails.get_url(device_uid=self.second_device.uid),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "----")
