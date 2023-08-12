from test.pages.common import DeviceGroupDelete, DeviceGroupList
from test.utils.helpers import client_login, create_member, page_in_response
from typing import *

from django.test import TestCase

from devices.models import DeviceGroup

FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="first_member",
    password="test_password",
)

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="second_member",
    password="test_password",
)

FIRST_DEVICE_GROUPS_DATA: Final[List[Dict[str, str]]] = [
    dict(
        name="test_group_1",
        description="first member test description 1",
    ),
    dict(
        name="test_group_2",
        description="first member test description 2",
    ),
    dict(
        name="test_group_3",
        description="first member test description 3",
    ),
    dict(
        name="test_group_4",
        description="first member test description 4",
    ),
]

SECOND_DEVICE_GROUPS_DATA: Final[List[Dict[str, str]]] = [
    dict(
        name="test_group_1",
        description="second member test description 1",
    ),
    dict(
        name="test_group_2",
        description="second member test description 2",
    ),
    dict(
        name="test_group_5",
        description="second member test description 5",
    ),
    dict(
        name="test_group_6",
        description="second member test description 6",
    ),
]


class BaseDeviceGroupDeleteTestCase(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(**FIRST_MEMBER)
        self.second_member = create_member(**SECOND_MEMBER)

        self.first_device_groups = DeviceGroup.objects.bulk_create(
            [
                DeviceGroup(**group_data, owner=self.first_member)
                for group_data in FIRST_DEVICE_GROUPS_DATA
            ],
            ignore_conflicts=True,
        )

        self.second_device_groups = DeviceGroup.objects.bulk_create(
            [
                DeviceGroup(**group_data, owner=self.second_member)
                for group_data in SECOND_DEVICE_GROUPS_DATA
            ],
            ignore_conflicts=True,
        )

        client_login(self.client, FIRST_MEMBER)

        return super().setUp()


class TestDeviceGroupDeleteRendering(BaseDeviceGroupDeleteTestCase):
    def test_device_group_delete_rendering(self):
        """Test device group delete page renders correctly"""
        # Get the name of the first device group
        device_group_name = FIRST_DEVICE_GROUPS_DATA[0]["name"]

        # Get the url for deleting the device group
        url = DeviceGroupDelete.get_url(group_name=device_group_name)

        # Send the request
        response = self.client.get(url)

        # check rendered page
        self.assertEqual(response.status_code, 200)
        self.assertTrue(page_in_response(DeviceGroupDelete, response)[0])
        self.assertContains(response, device_group_name)


class TestDeviceGroupDeleteForm(BaseDeviceGroupDeleteTestCase):
    def test_device_group_delete_form(self):
        """Test device group delete form has correct fields"""
        # Get the first device group.
        group_name = FIRST_DEVICE_GROUPS_DATA[0]["name"]

        # Get the URL to delete this device group.
        url = DeviceGroupDelete.get_url(group_name=group_name)

        # Get the delete confirmation form.
        response = self.client.get(url)
        form = response.context.get("form")

        # check form
        self.assertEqual(len(form.fields), 1)
        self.assertEqual(form.fields["password"].label, "Password")
        self.assertEqual(form.fields["password"].required, True)
        self.assertEqual(form.fields["password"].initial, None)


class TestDeviceGroupDeleteView(BaseDeviceGroupDeleteTestCase):
    def test_device_group_delete_remove_device(self):
        """Test deleting a device group removes the device from the group list, and from he member's device group set"""
        # Get the name of the device group to be deleted.
        device_group_name = FIRST_DEVICE_GROUPS_DATA[0]["name"]

        # Get the number of device groups the first member is a member of.
        member_groups = self.first_member.devicegroup_set.count()

        # Delete the device group.
        response = self.client.post(
            DeviceGroupDelete.get_url(group_name=device_group_name),
            data=dict(
                password=FIRST_MEMBER["password"],
            ),
            follow=True,
        )
        # reload first member data
        self.first_member.refresh_from_db()

        # check response
        self.assertGreater(
            member_groups, 0, "Member should have at least one device group"
        )
        self.assertRedirects(
            response, DeviceGroupList.get_url(), 302, 200, fetch_redirect_response=True
        )
        self.assertEqual(self.first_member.devicegroup_set.count(), member_groups - 1)

        # Get the deleted device group; should not exist.
        self.assertIsNone(
            self.first_member.devicegroup_set.filter(name=device_group_name).first(),
            "Device group should have been deleted from member's device group set",
        )
        self.assertIsNone(
            DeviceGroup.objects.filter(
                name=device_group_name, owner=self.first_member
            ).first(),
            "Device group should have been deleted from database",
        )

    def test_device_group_delete_other_member_404(self):
        """Test deleting a device group that belongs to another member returns 404"""
        device_group_name = SECOND_DEVICE_GROUPS_DATA[-1]["name"]
        first_member_groups = self.first_member.devicegroup_set.count()
        second_member_groups = self.second_member.devicegroup_set.count()
        response = self.client.post(
            DeviceGroupDelete.get_url(group_name=device_group_name),
            follow=True,
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.first_member.devicegroup_set.count(), first_member_groups)
        self.assertEqual(
            self.second_member.devicegroup_set.count(), second_member_groups
        )
