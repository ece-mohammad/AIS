from test.utils.helpers import client_login, client_logout, create_member
from typing import *

from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from api.serializers import DeviceGroupSerializer
from devices.models import DeviceGroup


FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="test_user_1",
    password="test password",
)

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="test_user_2",
    password="test password",
)

FIRST_MEMBER_GROUPS: Final[List[DeviceGroup]] = [
    DeviceGroup(name="test_group_1", description="test group 1 description"),
    DeviceGroup(name="test_group_2", description="test group 2 description"),
    DeviceGroup(name="test_group_3", description="test group 3 description"),
    DeviceGroup(name="test_group_4", description="test group 4 description"),
    DeviceGroup(name="test_group_5", description="test group 5 description"),
]


# -----------------------------------------------------------------------------
# Base Test classes (common set ups)
# -----------------------------------------------------------------------------

class BaseDeviceGroupsAPIViewListTestCase(APITestCase):
    def setUp(self):
        self.url = reverse_lazy("api:groups_list")
        self.first_member = create_member(**FIRST_MEMBER)
        
        for group in FIRST_MEMBER_GROUPS:
            group.owner = self.first_member
            group.save()
        
        self.second_member = create_member(**SECOND_MEMBER)
        
        client_login(self.client, FIRST_MEMBER)


class BaseDeviceGroupsAPIViewDetailsTestCase(BaseDeviceGroupsAPIViewListTestCase):
    def setUp(self):
        ret = super().setUp()
        url = reverse_lazy("api:groups_list")
        request = APIRequestFactory().get(url)
        request.user = self.first_member
        self.device_group = DeviceGroupSerializer(self.first_member.devicegroup_set.first(), context={"request": request})
        self.url = reverse_lazy(
            "api:group_details", 
            kwargs=dict(
                pk=self.device_group["id"].value
            )
        )
        return ret


# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------

class TestDeviceGroupsAPISerializer(BaseDeviceGroupsAPIViewListTestCase):
    def setUp(self) -> None:
        ret = super().setUp()
        request_factory = APIRequestFactory()
        request_factory.default_format = "json"
        self.request = request_factory.get(self.url)
        self.request.user = self.first_member
        self.group_data = dict(
            name="test_device_group",
            description="test device group description",
            owner_id=self.first_member.id,
            creation_date=timezone.now(),
        )
        return ret
    
    def test_api_device_group_serializer_fields(self):
        serializer = DeviceGroupSerializer()
        
        self.assertIsNotNone(serializer.fields.get("url"))
        self.assertIsNotNone(serializer.fields.get("name"))
        self.assertIsNotNone(serializer.fields.get("description"))
        self.assertIsNotNone(serializer.fields.get("creation_date"))
        self.assertIsNotNone(serializer.fields.get("id"))
        self.assertIsNotNone(serializer.fields.get("owner_id"))
        
        
        self.assertIsNotNone(serializer.fields.get("name"))
        self.assertIsNotNone(serializer.fields.get("description"))
        self.assertIsNotNone(serializer.fields.get("creation_date"))
        self.assertIsNotNone(serializer.fields.get("owner_id"))

    def test_api_device_group_serializer_invalid_name(self):
        group_name_with_spaces = self.group_data.copy()
        group_name_with_spaces["name"] = "name with spaces"
        group_name_with_spaces_serializer = DeviceGroupSerializer(data=group_name_with_spaces)
        
        group_with_empty_name = self.group_data.copy()
        group_with_empty_name["name"] = ""
        group_with_empty_name_serializer = DeviceGroupSerializer(data=group_with_empty_name)
        
        self.assertFalse(group_name_with_spaces_serializer.is_valid())
        self.assertIn("name", group_name_with_spaces_serializer.errors)
        
        self.assertFalse(group_with_empty_name_serializer.is_valid())
        self.assertIn("name", group_with_empty_name_serializer.errors)

    def test_api_device_group_serializer_invalid_user_id(self):
        group_with_invalid_owner_id = self.group_data.copy()
        group_with_invalid_owner_id["owner_id"] = -1
        serializer = DeviceGroupSerializer(data=group_with_invalid_owner_id)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn("owner_id", serializer.errors)

    def test_api_device_group_serializer_invalid_creation_date(self):
        group_with_invalid_creation_date = self.group_data.copy()
        group_with_invalid_creation_date["creation_date"] = "invalid date"
        serializer = DeviceGroupSerializer(data=group_with_invalid_creation_date)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn("creation_date", serializer.errors)

    def test_api_device_group_serializer_future_creation_date(self):
        group_with_future_creation_date = self.group_data.copy()
        group_with_future_creation_date["creation_date"] = timezone.now() + timezone.timedelta(days=1)
        serializer = DeviceGroupSerializer(data=group_with_future_creation_date)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn("creation_date", serializer.errors)

    def test_api_device_group_serializer_creation_date_default_value(self):
        group_with_no_creation_date = self.group_data.copy()
        group_with_no_creation_date.pop("creation_date", None)
        serializer = DeviceGroupSerializer(data=group_with_no_creation_date)
        is_valid = serializer.is_valid()
        creation_date = serializer.validated_data.get("creation_date", None)
        now = timezone.now()
        
        self.assertTrue(is_valid)
        self.assertIsNotNone(creation_date)
        self.assertEqual(creation_date.year, now.year)
        self.assertEqual(creation_date.month, now.month)
        self.assertEqual(creation_date.day, now.day)
        self.assertEqual(creation_date.hour, now.hour)
        self.assertEqual(creation_date.minute, now.minute)
        self.assertEqual(creation_date.second, now.second)


class TestDeviceGroupsAPIViewList(BaseDeviceGroupsAPIViewListTestCase):
    def test_api_device_group_list_anonymous_user(self):
        client_logout(self.client)
        response = self.client.get(
            self.url,
            follow=True,
        )
        error = response.data["detail"]
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(error, "Authentication credentials were not provided.")
        self.assertEqual(error.code, "not_authenticated")

    def test_api_device_group_list_get_device_groups(self):
        response = self.client.get(
            self.url, 
            data=dict(
                format="json"
            ),
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        for index, dev in enumerate(self.first_member.devicegroup_set.all().order_by("name"), start=0):
            self.assertEqual(response.data[index]["name"], dev.name)

    def test_api_device_group_list_create_device_group(self):
        new_group_data = dict(
            name="test_device_group",
            description="test device group description",
            owner_id=self.first_member.id,
            creation_date=timezone.now(),
        )
        device_count_before = self.first_member.devicegroup_set.count()
        response = self.client.post(
            self.url,
            data=new_group_data,
            follow=True,
        )
        device_count_after = self.first_member.devicegroup_set.count()
        last_device = DeviceGroupSerializer(instance=self.first_member.devicegroup_set.last(), context={"request": response.wsgi_request})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(device_count_before + 1, device_count_after)
        self.assertEqual(response.data["name"], last_device["name"].value)
        self.assertEqual(response.data["description"], last_device["description"].value)
        self.assertEqual(response.data["owner_id"], last_device["owner_id"].value)
        self.assertEqual(response.data["creation_date"], last_device["creation_date"].value)

    def test_api_device_group_list_creation_time_is_optional(self):
        new_group_data = dict(
            name="test_device_group",
            description="test device group description",
            owner_id=self.first_member.id,
        )
        
        device_count_before = self.first_member.devicegroup_set.count()
        response = self.client.post(
            self.url,
            data=new_group_data,
            follow=True,
        )
        device_count_after = self.first_member.devicegroup_set.count()
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(device_count_before + 1, device_count_after)

    def test_api_device_group_list_own_device_groups(self):
        client_logout(self.client)
        client_login(self.client, SECOND_MEMBER)
        response = self.client.get(
            self.url,
            follow=True,
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])


class TestDeviceGroupsViewAPIDetails(BaseDeviceGroupsAPIViewDetailsTestCase):
    def test_api_device_group_details_get_device_group(self):
        response = self.client.get(
            self.url,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.device_group["name"].value)
        self.assertEqual(response.data["description"], self.device_group["description"].value)
        self.assertEqual(response.data["owner_id"], self.device_group["owner_id"].value)
        self.assertEqual(response.data["creation_date"], self.device_group["creation_date"].value)

    def test_api_device_group_details_non_existent_group_is_404(self):
        response = self.client.get(
            reverse_lazy("api:group_details", kwargs=dict(pk=999999)),
            follow=True,
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_device_group_details_another_member_group_is_404(self):
        client_logout(self.client)
        client_login(self.client, SECOND_MEMBER)
        
        response = self.client.get(
            self.url,
            follow=True
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_device_group_details_patch_is_not_supported(self):
        response = self.client.patch(
            self.url,
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_api_device_group_details_put_is_not_supported(self):
        response = self.client.put(
            self.url,
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_api_device_group_details_delete_is_not_supported(self):
        response = self.client.delete(
            self.url,
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
