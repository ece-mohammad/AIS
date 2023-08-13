from typing import *

from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from accounts.models import Member
from api.v1.serializers import DeviceGroupHyperlinkedField, DeviceGroupSerializer
from devices.models import DeviceGroup

# -----------------------------------------------------------------------------
# Base Test classes (common set ups)
# -----------------------------------------------------------------------------


class BaseDeviceGroupsAPIViewListTestCase(APITestCase):
    fixtures = ["api/test_fixture.json"]

    def setUp(self):
        self.first_member = Member.objects.filter(is_active=True).first()
        self.second_member = Member.objects.filter(
            Q(is_active=True) & ~Q(id=self.first_member.id)
        ).first()
        self.inactive_member = Member.objects.filter(is_active=False).first()
        self.second_member = Member.objects.get(pk=2)
        self.device_group = self.first_member.devicegroup_set.first()
        self.url = reverse_lazy(
            "api:v1:groups_list", kwargs=dict(username=self.first_member.username)
        )
        self.client.force_login(self.first_member)


class BaseDeviceGroupsAPIViewDetailsTestCase(BaseDeviceGroupsAPIViewListTestCase):
    def setUp(self):
        ret = super().setUp()
        url = reverse_lazy(
            "api:v1:groups_list", kwargs=dict(username=self.first_member.username)
        )
        request = APIRequestFactory().get(url)
        request.user = self.first_member
        self.serialized_device_group = DeviceGroupSerializer(
            self.first_member.devicegroup_set.first(), context={"request": request}
        )
        self.url = reverse_lazy(
            "api:v1:group_details",
            kwargs=dict(
                username=self.first_member.username,
                group_name=self.serialized_device_group["name"].value,
            ),
        )
        return ret


# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------
class TestDeviceGroupsHyperlinkedField(BaseDeviceGroupsAPIViewListTestCase):
    def setUp(self):
        ret = super().setUp()
        self.url_field = DeviceGroupHyperlinkedField()
        self.view_name = "api:v1:group_details"
        self.lookup_field = "name"
        self.lookup_url_kwarg = "group_name"
        self.url = reverse_lazy(
            self.view_name,
            kwargs={
                "username": getattr(self.first_member, "username"),
                self.lookup_url_kwarg: getattr(self.device_group, self.lookup_field),
            },
        )
        response = self.client.get(self.url)
        self.request = response.wsgi_request
        return ret

    def test_device_group_hyperlink_field_assert(self):
        self.url_field.assert_device_group_link_field(
            self.device_group, self.view_name, self.lookup_field, self.lookup_url_kwarg
        )

    def test_device_group_hyperlink_field_assert_invalid(self):
        with self.assertRaises(ValueError):
            self.url_field.assert_device_group_link_field(
                None, self.view_name, self.lookup_field, self.lookup_url_kwarg
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_group_link_field(
                self.device_group,
                "invalid_view_name",
                self.lookup_field,
                self.lookup_url_kwarg,
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_group_link_field(
                self.device_group,
                self.view_name,
                "invalid_lookup_field",
                self.lookup_url_kwarg,
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_group_link_field(
                self.device_group,
                self.view_name,
                self.lookup_field,
                "invalid_lookup_url_kwarg",
            )

    def test_device_group_hyperlink_field_url_kwargs_from_instance(self):
        url_kwargs = self.url_field.get_device_group_url_kwargs_from_instance(
            self.device_group
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.device_group, self.lookup_field),
        )

    def test_device_group_hyperlink_field_url_kwargs_from_request(self):
        url_kwargs = self.url_field.get_device_group_url_kwargs_from_request(
            self.request
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.device_group, self.lookup_field),
        )

    def test_device_group_hyperlink_field_url_kwargs(self):
        url_kwargs = self.url_field.get_device_group_url_kwargs(
            self.device_group, self.request
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.device_group, self.lookup_field),
        )

    def test_device_group_hyperlink_field_url_kwargs_none_instance(self):
        url_kwargs = self.url_field.get_device_group_url_kwargs(None, self.request)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.device_group, self.lookup_field),
        )

    def test_device_group_hyperlink_field_url_kwargs_none_request(self):
        url_kwargs = self.url_field.get_device_group_url_kwargs(self.device_group, None)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.device_group, self.lookup_field),
        )

    def test_device_group_hyperlink_field_url_kwargs_none_instance_and_request(self):
        with self.assertRaises(AttributeError):
            self.url_field.get_device_group_url_kwargs(None, None)


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
            owner=self.first_member,
            creation_date=timezone.now(),
        )
        return ret

    def test_api_device_group_serializer_fields(self):
        serializer = DeviceGroupSerializer()

        self.assertIsNotNone(serializer.fields.get("url"))
        self.assertIsNotNone(serializer.fields.get("name"))
        self.assertIsNotNone(serializer.fields.get("id"))
        self.assertIsNotNone(serializer.fields.get("description"))
        self.assertIsNotNone(serializer.fields.get("creation_date"))
        self.assertIsNotNone(serializer.fields.get("owner"))
        self.assertIsNotNone(serializer.fields.get("device_set"))

    def test_api_device_group_serializer_invalid_name(self):
        group_name_with_spaces = self.group_data.copy()
        group_name_with_spaces["name"] = "name with spaces"
        group_name_with_spaces_serializer = DeviceGroupSerializer(
            data=group_name_with_spaces
        )

        group_with_empty_name = self.group_data.copy()
        group_with_empty_name["name"] = ""
        group_with_empty_name_serializer = DeviceGroupSerializer(
            data=group_with_empty_name
        )

        self.assertFalse(group_name_with_spaces_serializer.is_valid())
        self.assertIn("name", group_name_with_spaces_serializer.errors)

        self.assertFalse(group_with_empty_name_serializer.is_valid())
        self.assertIn("name", group_with_empty_name_serializer.errors)

    def test_api_device_group_serializer_invalid_creation_date(self):
        group_with_invalid_creation_date = self.group_data.copy()
        group_with_invalid_creation_date["creation_date"] = "invalid date"
        serializer = DeviceGroupSerializer(data=group_with_invalid_creation_date)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("creation_date", serializer.errors)

    def test_api_device_group_serializer_future_creation_date(self):
        group_with_future_creation_date = self.group_data.copy()
        group_with_future_creation_date[
            "creation_date"
        ] = timezone.now() + timezone.timedelta(days=1)
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

    def test_api_device_group_serializer_create(self):
        new_device_group_data = dict(
            name="test_device_group",
            description="test device group description",
            creation_date=timezone.now(),
            device_set=[],
        )

        serializer = DeviceGroupSerializer(
            data=new_device_group_data, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        new_device_group = serializer.save(
            owner=self.first_member,
            creation_date=new_device_group_data["creation_date"],
        )

        self.assertEqual(is_valid, True)
        self.assertEqual(new_device_group.name, new_device_group_data["name"])
        self.assertEqual(
            new_device_group.description, new_device_group_data["description"]
        )
        self.assertEqual(new_device_group.owner, self.first_member)
        self.assertEqual(
            new_device_group.creation_date, new_device_group_data["creation_date"]
        )
        self.assertEqual(new_device_group.device_set.count(), 0)

    def test_api_device_group_serializer_create_min_data(self):
        min_device_group_data = dict(
            name="test_device_group",
        )

        device_count_before = DeviceGroup.objects.count()
        serializer = DeviceGroupSerializer(
            data=min_device_group_data, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        new_device_group = serializer.save(owner=self.first_member)
        last_device_group = DeviceGroup.objects.last()
        device_count_after = DeviceGroup.objects.count()

        self.assertEqual(is_valid, True)
        self.assertEqual(device_count_after - 1, device_count_before)

        self.assertEqual(new_device_group.name, min_device_group_data["name"])
        self.assertEqual(new_device_group.owner, self.first_member)
        self.assertEqual(new_device_group.creation_date.date(), timezone.now().date())
        self.assertEqual(new_device_group.device_set.count(), 0)

        self.assertEqual(last_device_group.pk, new_device_group.pk)
        self.assertEqual(last_device_group.name, new_device_group.name)
        self.assertEqual(last_device_group.description, new_device_group.description)
        self.assertEqual(last_device_group.owner, new_device_group.owner)
        self.assertEqual(
            last_device_group.creation_date, new_device_group.creation_date
        )


class TestDeviceGroupsAPIViewList(BaseDeviceGroupsAPIViewListTestCase):
    def test_api_device_group_list_anonymous_user(self):
        self.client.logout()
        response = self.client.get(
            self.url,
            follow=True,
        )
        error = response.data["detail"]

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(error, "Authentication credentials were not provided.")
        self.assertEqual(error.code, "not_authenticated")

    def test_api_device_group_list_get_device_groups(self):
        response = self.client.get(self.url, data=dict(format="json"), follow=True)

        self.assertEqual(response.status_code, 200)
        for index, group in enumerate(
            self.first_member.devicegroup_set.all().order_by("name"), start=0
        ):
            self.assertEqual(response.data[index]["name"], group.name)

    def test_api_device_group_list_create_device_group(self):
        new_group_data = dict(
            name="test_device_group",
            description="test device group description",
            owner=self.first_member,
            creation_date=timezone.now(),
        )
        device_count_before = self.first_member.devicegroup_set.count()
        response = self.client.post(
            self.url,
            data=new_group_data,
            follow=True,
        )
        device_count_after = self.first_member.devicegroup_set.count()
        last_device = DeviceGroupSerializer(
            instance=self.first_member.devicegroup_set.last(),
            context={"request": response.wsgi_request},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(device_count_before + 1, device_count_after)
        self.assertEqual(response.data["name"], last_device["name"].value)
        self.assertEqual(response.data["description"], last_device["description"].value)
        self.assertEqual(response.data["owner"], last_device["owner"].value)
        self.assertEqual(
            response.data["creation_date"], last_device["creation_date"].value
        )

    def test_api_device_group_list_create_device_group_min_data(self):
        new_group_data = dict(
            name="test_device_group",
        )
        device_count_before = self.first_member.devicegroup_set.count()
        response = self.client.post(
            self.url,
            data=new_group_data,
            follow=True,
        )
        device_count_after = self.first_member.devicegroup_set.count()
        last_device = DeviceGroupSerializer(
            instance=self.first_member.devicegroup_set.last(),
            context={"request": response.wsgi_request},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(device_count_before + 1, device_count_after)
        self.assertEqual(response.data["name"], last_device["name"].value)
        self.assertEqual(response.data["description"], last_device["description"].value)
        self.assertEqual(response.data["owner"], last_device["owner"].value)
        self.assertEqual(
            response.data["creation_date"], last_device["creation_date"].value
        )

    def test_api_device_group_list_creation_time_is_optional(self):
        new_group_data = dict(
            name="test_device_group",
            description="test device group description",
            owner=self.first_member,
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

    def test_api_device_group_list_another_member_is_403(self):
        self.client.logout()
        self.client.force_login(self.second_member)

        response = self.client.get(
            self.url,
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )


class TestDeviceGroupsAPIViewDetails(BaseDeviceGroupsAPIViewDetailsTestCase):
    def test_api_device_group_details_get_device_group(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["name"], self.serialized_device_group["name"].value
        )
        self.assertEqual(
            response.data["description"],
            self.serialized_device_group["description"].value,
        )
        self.assertEqual(
            response.data["owner"], self.serialized_device_group["owner"].value
        )
        self.assertEqual(
            response.data["creation_date"],
            self.serialized_device_group["creation_date"].value,
        )

    def test_api_device_group_details_non_existent_group_is_404(self):
        response = self.client.get(
            reverse_lazy(
                "api:v1:group_details",
                kwargs=dict(
                    username=self.first_member.username, group_name="non_existent_group"
                ),
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_device_group_details_another_member_group_is_403(self):
        self.client.logout()
        self.client.force_login(self.second_member)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_device_group_details_put_modifies_device_group(self):
        device_group_data = dict(
            name=f"new_{self.device_group.name}",
            description=f"new {self.device_group.description}",
        )
        response = self.client.put(
            self.url,
            data=device_group_data,
        )
        self.device_group.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.device_group.name, device_group_data["name"])
        self.assertEqual(self.device_group.description, device_group_data["description"])

    def test_api_device_group_details_put_name_is_required(self):
        device_group_data = dict(
            description=f"new {self.device_group.description}",
        )
        response = self.client.put(
            self.url,
            data=device_group_data,
        )
        self.device_group.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_device_group_details_put_no_data_is_400(self):
        response = self.client.put(
            self.url,
            data=dict(),
        )
        self.device_group.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_device_group_details_put_name_with_spaces_is_400(self):
        device_group_data = dict(
            name="name with spaces",
            description=f"new {self.device_group.description}",
        )
        response = self.client.put(
            self.url,
            data=device_group_data,
        )
        self.device_group.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_api_device_group_details_put_empty_name_is_400(self):
        device_group_data = dict(
            name="",
            description=f"new {self.device_group.description}",
        )
        response = self.client.put(
            self.url,
            data=device_group_data,
        )
        self.device_group.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_device_group_details_patch_modify_name(self):
        new_name = f"new_{self.device_group.name}"
        old_description = self.device_group.description
        response = self.client.patch(
            self.url,
            data=dict(name=new_name),
        )
        self.device_group.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.device_group.name, new_name)
        self.assertEqual(self.device_group.description, old_description)
        
    def test_api_device_group_details_patch_modify_description(self):
        old_name = self.device_group.name
        new_description = f"new {self.device_group.description}"
        response = self.client.patch(
            self.url,
            data=dict(description=new_description),
        )
        self.device_group.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.device_group.name, old_name)
        self.assertEqual(self.device_group.description, new_description)

    def test_api_device_group_details_patch_name_with_spaces_is_400(self):
        new_name = "new name with spaces"
        old_name = self.device_group.name
        response = self.client.patch(
            self.url,
            data=dict(name=new_name),
        )
        self.device_group.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.device_group.name, old_name)
    
    def test_api_device_group_details_delete_removes_device_group(self):
        response = self.client.delete(
            self.url,
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(DeviceGroup.DoesNotExist):
            self.device_group.refresh_from_db()
