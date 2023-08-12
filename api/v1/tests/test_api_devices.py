from typing import *

from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from accounts.models import Member
from api.v1.serializers import DeviceHyperlinkedField, DeviceSerializer
from devices.models import Device

# -----------------------------------------------------------------------------
# Base Test classes (common set ups)
# -----------------------------------------------------------------------------


class BaseDeviceAPIViewListTestCase(APITestCase):
    fixtures = ["api/test_fixture.json"]

    def setUp(self):
        self.first_member = Member.objects.filter(is_active=True).first()
        self.second_member = Member.objects.filter(
            Q(is_active=True) & ~Q(id=self.first_member.id)
        ).first()
        self.inactive_member = Member.objects.filter(is_active=False).first()

        self.first_group = self.first_member.devicegroup_set.first()
        self.first_device = self.first_group.device_set.first()

        self.url = reverse_lazy(
            "api:v1:devices_list",
            kwargs=dict(
                username=self.first_member.username, group_name=self.first_group.name
            ),
        )

        device_name = "test_device_new"
        self.device_data = dict(
            name=device_name,
            uid=Device.generate_device_uid(
                f"{self.first_member.username}-{self.first_group.name}-{device_name}"
            ),
            group=self.first_group,
            date_added=timezone.now(),
        )

        self.client.force_login(self.first_member)


class BaseDeviceAPIViewDetailsTestCase(BaseDeviceAPIViewListTestCase):
    def setUp(self):
        ret = super().setUp()
        request = APIRequestFactory().get(self.url)
        request.user = self.first_member
        self.serialized_device = DeviceSerializer(
            instance=self.first_device, context={"request": request}
        )
        self.url = reverse_lazy(
            "api:v1:device_details",
            kwargs=dict(
                username=self.first_member.username,
                group_name=self.first_group.name,
                device_uid=self.first_device.uid,
            ),
        )
        return ret


# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------
class TestDeviceHyperlinkedField(BaseDeviceAPIViewListTestCase):
    def setUp(self):
        ret = super().setUp()
        self.url_field = DeviceHyperlinkedField()
        self.view_name = "api:v1:device_details"
        self.lookup_field = "uid"
        self.lookup_url_kwarg = "device_uid"
        self.url = reverse_lazy(
            self.view_name,
            kwargs={
                "username": getattr(self.first_member, "username"),
                "group_name": getattr(self.first_group, "name"),
                self.lookup_url_kwarg: getattr(self.first_device, self.lookup_field),
            },
        )
        response = self.client.get(self.url)
        self.request = response.wsgi_request
        return ret

    def test_device_hyperlink_field_assert(self):
        self.url_field.assert_device_link_field(
            self.first_device, self.view_name, self.lookup_field, self.lookup_url_kwarg
        )

    def test_device_hyperlink_field_assert_invalid(self):
        with self.assertRaises(ValueError):
            self.url_field.assert_device_link_field(
                None, self.view_name, self.lookup_field, self.lookup_url_kwarg
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_link_field(
                self.first_device,
                "invalid_view_name",
                self.lookup_field,
                self.lookup_url_kwarg,
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_link_field(
                self.first_device,
                self.view_name,
                "invalid_lookup_field",
                self.lookup_url_kwarg,
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_link_field(
                self.first_device,
                self.view_name,
                self.lookup_field,
                "invalid_lookup_url_kwarg",
            )

    def test_device_hyperlink_field_url_kwargs_from_instance(self):
        url_kwargs = self.url_field.get_device_url_kwargs_from_instance(
            self.first_device
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            str(getattr(self.first_device, self.lookup_field)),
        )

    def test_device_hyperlink_field_url_kwargs_from_request(self):
        url_kwargs = self.url_field.get_device_url_kwargs_from_request(self.request)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            str(getattr(self.first_device, self.lookup_field)),
        )

    def test_device_hyperlink_field_url_kwargs(self):
        url_kwargs = self.url_field.get_device_url_kwargs(
            self.first_device, self.request
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            str(getattr(self.first_device, self.lookup_field)),
        )

    def test_device_hyperlink_field_url_kwargs_none_instance(self):
        url_kwargs = self.url_field.get_device_url_kwargs(None, self.request)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            str(getattr(self.first_device, self.lookup_field)),
        )

    def test_device_hyperlink_field_url_kwargs_none_request(self):
        url_kwargs = self.url_field.get_device_url_kwargs(self.first_device, None)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            str(getattr(self.first_device, self.lookup_field)),
        )

    def test_device_hyperlink_field_url_kwargs_none_instance_and_request(self):
        with self.assertRaises(AttributeError):
            self.url_field.get_device_url_kwargs(None, None)


class TestDeviceAPISerializer(BaseDeviceAPIViewListTestCase):
    def setUp(self) -> None:
        ret = super().setUp()
        request_factory = APIRequestFactory()
        request_factory.default_format = "json"
        self.request = request_factory.get(self.url)
        self.request.user = self.first_member
        return ret

    def test_api_device_serializer_fields(self):
        serializer = DeviceSerializer()

        self.assertIsNotNone(serializer.fields.get("url"))
        self.assertIsNotNone(serializer.fields.get("name"))
        self.assertIsNotNone(serializer.fields.get("uid"))
        self.assertIsNotNone(serializer.fields.get("date_added"))
        self.assertIsNotNone(serializer.fields.get("is_active"))
        self.assertIsNotNone(serializer.fields.get("group"))
        self.assertIsNotNone(serializer.fields.get("devicedata_set"))

    def test_api_device_serializer_invalid_name(self):
        device_name_with_spaces = self.device_data.copy()
        device_name_with_spaces["name"] = "name with spaces"
        device_name_with_spaces_serializer = DeviceSerializer(
            data=device_name_with_spaces
        )

        device_with_empty_name = self.device_data.copy()
        device_with_empty_name["name"] = ""
        device = DeviceSerializer(data=device_with_empty_name)

        self.assertFalse(device_name_with_spaces_serializer.is_valid())
        self.assertIn("name", device_name_with_spaces_serializer.errors)

        self.assertFalse(device.is_valid())
        self.assertIn("name", device.errors)

    def test_api_device_serializer_invalid_date_added(self):
        device_with_invalid_date_added = self.device_data.copy()
        device_with_invalid_date_added["date_added"] = "invalid date"
        serializer = DeviceSerializer(data=device_with_invalid_date_added)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("date_added", serializer.errors)

    def test_api_device_serializer_future_date_added(self):
        device_with_future_date_added = self.device_data.copy()
        device_with_future_date_added[
            "date_added"
        ] = timezone.now() + timezone.timedelta(days=1)
        serializer = DeviceSerializer(data=device_with_future_date_added)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("date_added", serializer.errors)

    def test_api_device_serializer_date_added_default_value(self):
        device_with_no_date_added = self.device_data.copy()
        device_with_no_date_added.pop("date_added", None)
        serializer = DeviceSerializer(data=device_with_no_date_added)
        is_valid = serializer.is_valid()
        date_added = serializer.validated_data.get("date_added", None)

        self.assertTrue(is_valid)
        self.assertIsNone(date_added)

    def test_api_device_serializer_create(self):
        new_device_group_data = self.device_data.copy()

        serializer = DeviceSerializer(
            data=new_device_group_data, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        new_device_group = serializer.save(
            group=self.first_group, date_added=new_device_group_data["date_added"]
        )

        self.assertEqual(is_valid, True)
        self.assertEqual(new_device_group.name, new_device_group_data["name"])
        self.assertEqual(new_device_group.uid, new_device_group_data["uid"])
        self.assertEqual(new_device_group.group, self.first_group)
        self.assertEqual(
            new_device_group.date_added, new_device_group_data["date_added"]
        )
        self.assertEqual(new_device_group.devicedata_set.count(), 0)

    def test_api_device_serializer_create_uid_is_optional(self):
        new_device_group_data = self.device_data.copy()
        uid = new_device_group_data.pop("uid", None)

        serializer = DeviceSerializer(
            data=new_device_group_data, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        new_device_group = serializer.save(
            group=self.first_group, date_added=new_device_group_data["date_added"]
        )

        self.assertEqual(is_valid, True)
        self.assertEqual(new_device_group.name, new_device_group_data["name"])
        self.assertEqual(new_device_group.uid, uid)
        self.assertEqual(new_device_group.group, self.first_group)
        self.assertEqual(
            new_device_group.date_added, new_device_group_data["date_added"]
        )
        self.assertEqual(new_device_group.devicedata_set.count(), 0)

    def test_api_device_serializer_create_date_added_is_optional(self):
        new_device_group_data = self.device_data.copy()
        new_device_group_data.pop("date_added", None)

        serializer = DeviceSerializer(
            data=new_device_group_data, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        new_device_group = serializer.save(group=self.first_group)

        self.assertEqual(is_valid, True)
        self.assertEqual(new_device_group.name, new_device_group_data["name"])
        self.assertEqual(new_device_group.uid, new_device_group_data["uid"])
        self.assertEqual(new_device_group.group, self.first_group)
        self.assertEqual(new_device_group.devicedata_set.count(), 0)


class TestDeviceAPIViewList(BaseDeviceAPIViewListTestCase):
    def test_api_device_list_anonymous_user(self):
        self.client.logout()
        response = self.client.get(
            self.url,
            follow=True,
        )
        error = response.data["detail"]

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(error, "Authentication credentials were not provided.")
        self.assertEqual(error.code, "not_authenticated")

    def test_api_device_list_get_device(self):
        response = self.client.get(self.url, data=dict(format="json"), follow=True)

        self.assertEqual(response.status_code, 200)
        for index, dev in enumerate(
            self.first_group.device_set.all().order_by("name"), start=0
        ):
            self.assertEqual(response.data[index]["name"], dev.name)

    def test_api_device_list_create_device(self):
        new_group_data = self.device_data.copy()
        device_count_before = self.first_group.device_set.count()
        response = self.client.post(
            self.url,
            data=new_group_data,
            follow=True,
        )
        device_count_after = self.first_group.device_set.count()
        last_device = DeviceSerializer(
            instance=Device.objects.last(), context={"request": response.wsgi_request}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(device_count_before + 1, device_count_after)
        self.assertEqual(response.data["name"], last_device["name"].value)
        self.assertEqual(response.data["uid"], last_device["uid"].value)
        self.assertEqual(response.data["group"], last_device["group"].value)
        self.assertEqual(response.data["date_added"], last_device["date_added"].value)

    def test_api_device_list_invalid_name_is_400(self):
        device_data = self.device_data.copy()
        device_data["name"] = "invalid name"
        device_count_before = self.first_group.device_set.count()
        response = self.client.post(
            self.url,
            data=device_data,
        )
        device_count_after = self.first_group.device_set.count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["name"][0].code, "invalid")
        self.assertEqual(device_count_before, device_count_after)

    def test_api_device_list_creation_time_is_optional(self):
        new_device_data = self.device_data.copy()
        new_device_data.pop("date_added", None)

        device_count_before = self.first_group.device_set.count()
        response = self.client.post(
            self.url,
            data=new_device_data,
            follow=True,
        )
        device_count_after = self.first_group.device_set.count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(device_count_before + 1, device_count_after)

    def test_api_device_list_another_member_is_403(self):
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


class TestDeviceViewAPIDetails(BaseDeviceAPIViewDetailsTestCase):
    def test_api_device_details_get_device(self):
        response = self.client.get(self.url, follow=True)

        device_data = DeviceSerializer(
            instance=self.first_device, context={"request": response.wsgi_request}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], device_data["name"].value)
        self.assertEqual(response.data["uid"], device_data["uid"].value)
        self.assertEqual(response.data["date_added"], device_data["date_added"].value)
        self.assertEqual(response.data["group"], device_data["group"].value)

    def test_api_device_details_non_existent_device_is_404(self):
        response = self.client.get(
            path=reverse_lazy(
                "api:v1:device_details",
                kwargs=dict(
                    username=self.first_member.username,
                    group_name=self.first_group.name,
                    device_uid="00000000-0000-0000-0000-000000000000",
                ),
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_device_details_another_member_device_is_403(self):
        self.client.logout()
        self.client.force_login(self.second_member)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_device_details_put_updates_device(self):
        device_data = dict(
            name=f"new_{self.first_device.name}",
            uid=self.first_device.uid,
            group=self.first_device.group.id,
            date_added=self.first_device.date_added,
        )
        response = self.client.put(
            self.url,
            data=device_data,
        )
        self.first_device.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.first_device.name, device_data["name"])

    def test_api_device_details_put_name_is_required(self):
        device_data = dict(
            uid=self.first_device.uid,
            group=self.first_device.group.id,
            date_added=self.first_device.date_added,
        )
        response = self.client.put(
            self.url,
            data=device_data,
        )
        self.first_device.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["name"][0].code, "required")

    def test_api_device_details_put_min_data(self):
        device_data = dict(
            name=f"new_{self.first_device.name}",
        )
        response = self.client.put(
            self.url,
            data=device_data,
        )
        self.first_device.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.first_device.name, device_data["name"])

    def test_api_device_details_patch_updates_device_name(self):
        device_data = dict(
            name=f"new_{self.first_device.name}"
        )
        response = self.client.patch(
            self.url,
            data=device_data,
        )
        self.first_device.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.first_device.name, device_data["name"])

    def test_api_device_details_patch_no_data_is_200(self):
        device_data = dict()
        old_device_name = self.first_device.name
        response = self.client.patch(
            self.url,
            data=device_data,
        )
        self.first_device.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.first_device.name, old_device_name)

    def test_api_device_details_patch_empty_name_is_400(self):
        device_data = dict(
            name=f""
        )
        old_device_name = self.first_device.name
        response = self.client.patch(
            self.url,
            data=device_data,
        )
        self.first_device.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.first_device.name, old_device_name)

    def test_api_device_details_patch_name_with_spaces_is_400(self):
        device_data = dict(
            name=f"new {self.first_device.name}"
        )
        old_device_name = self.first_device.name
        response = self.client.patch(
            self.url,
            data=device_data,
        )
        self.first_device.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.first_device.name, old_device_name)

    def test_api_device_details_delete_is_not_supported(self):
        response = self.client.delete(
            self.url,
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Device.DoesNotExist):
            self.first_device.refresh_from_db()
