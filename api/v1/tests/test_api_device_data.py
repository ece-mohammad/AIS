import json
from typing import *

from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from accounts.models import Member
from api.v1.serializers import DeviceDataHyperlinkedField, DeviceDataSerializer
from devices.models import Device, DeviceData, DeviceGroup

# -----------------------------------------------------------------------------
# Base Test classes (common set ups)
# -----------------------------------------------------------------------------


class BaseDeviceDataAPIViewListTestCase(APITestCase):
    fixtures = ["api/test_fixture.json"]

    def setUp(self):
        self.first_member: Member | None = Member.objects.filter(is_active=True).first()
        self.second_member: Member | None = Member.objects.filter(
            Q(is_active=True) & ~Q(id=self.first_member.id)
        ).first()
        self.inactive_member: Member | None = Member.objects.filter(
            is_active=False
        ).first()

        self.first_group: DeviceGroup = self.first_member.devicegroup_set.first()
        self.first_device: Device = self.first_group.device_set.first()
        self.first_device_data: DeviceData = self.first_device.devicedata_set.first()

        self.url: str = reverse_lazy(
            "api:v1:data_list",
            kwargs=dict(
                username=self.first_member.username,
                group_name=self.first_group.name,
                device_uid=self.first_device.uid,
            ),
        )

        self.data: Dict = dict(
            message={"foo": "bar"},
            date=timezone.now(),
        )

        self.client.force_login(self.first_member)


class BaseDeviceDataAPIViewDetailsTestCase(BaseDeviceDataAPIViewListTestCase):
    def setUp(self):
        ret = super().setUp()
        request = APIRequestFactory().get(self.url)
        request.user = self.first_member
        self.first_serialized_data: DeviceDataSerializer = DeviceDataSerializer(
            instance=self.first_device_data, context={"request": request}
        )
        self.url: str = reverse_lazy(
            "api:v1:data_details",
            kwargs=dict(
                username=self.first_member.username,
                group_name=self.first_group.name,
                device_uid=self.first_device.uid,
                data_id=self.first_device_data.id,
            ),
        )
        return ret


# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------
class TestDeviceDataHyperlinkedField(BaseDeviceDataAPIViewListTestCase):
    def setUp(self):
        ret = super().setUp()
        self.url_field = DeviceDataHyperlinkedField()
        self.view_name = "api:v1:data_details"
        self.lookup_field = "id"
        self.lookup_url_kwarg = "data_id"
        self.url = reverse_lazy(
            self.view_name,
            kwargs={
                "username": getattr(self.first_member, "username"),
                "group_name": getattr(self.first_group, "name"),
                "device_uid": getattr(self.first_device, "uid"),
                self.lookup_url_kwarg: getattr(self.first_device, self.lookup_field),
            },
        )
        response = self.client.get(self.url)
        self.request = response.wsgi_request
        return ret

    def test_device_data_hyperlink_field_assert(self):
        self.url_field.assert_device_data_link_field(
            self.first_device_data,
            self.view_name,
            self.lookup_field,
            self.lookup_url_kwarg,
        )

    def test_device_data_hyperlink_field_assert_invalid(self):
        with self.assertRaises(ValueError):
            self.url_field.assert_device_data_link_field(
                None, self.view_name, self.lookup_field, self.lookup_url_kwarg
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_data_link_field(
                self.first_device,
                "invalid_view_name",
                self.lookup_field,
                self.lookup_url_kwarg,
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_data_link_field(
                self.first_device,
                self.view_name,
                "invalid_lookup_field",
                self.lookup_url_kwarg,
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_device_data_link_field(
                self.first_device,
                self.view_name,
                self.lookup_field,
                "invalid_lookup_url_kwarg",
            )

    def test_device_data_hyperlink_field_url_kwargs_from_instance(self):
        url_kwargs = self.url_field.get_device_data_url_kwargs_from_instance(
            self.first_device_data
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_device_data, self.lookup_field),
        )

    def test_device_data_hyperlink_field_url_kwargs_from_request(self):
        url_kwargs = self.url_field.get_device_data_url_kwargs_from_request(
            self.request
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_device_data, self.lookup_field),
        )

    def test_device_data_hyperlink_field_url_kwargs(self):
        url_kwargs = self.url_field.get_device_data_url_kwargs(
            self.first_device_data, self.request
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_device_data, self.lookup_field),
        )

    def test_device_data_hyperlink_field_url_kwargs_none_instance(self):
        url_kwargs = self.url_field.get_device_data_url_kwargs(None, self.request)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_device_data, self.lookup_field),
        )

    def test_device_data_hyperlink_field_url_kwargs_none_request(self):
        url_kwargs = self.url_field.get_device_data_url_kwargs(
            self.first_device_data, None
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_device_data, self.lookup_field),
        )

    def test_device_data_hyperlink_field_url_kwargs_none_instance_and_request(self):
        with self.assertRaises(AttributeError):
            self.url_field.get_device_data_url_kwargs(None, None)


class TestDeviceDataAPISerializer(BaseDeviceDataAPIViewListTestCase):
    def setUp(self) -> None:
        ret = super().setUp()
        request_factory = APIRequestFactory()
        request_factory.default_format = "json"
        self.request = request_factory.get(self.url)
        self.request.user = self.first_member
        return ret

    def test_api_device_data_serializer_fields(self):
        serializer = DeviceDataSerializer()

        self.assertIsNotNone(serializer.fields.get("url"))
        self.assertIsNotNone(serializer.fields.get("id"))
        self.assertIsNotNone(serializer.fields.get("date"))
        self.assertIsNotNone(serializer.fields.get("message"))
        self.assertIsNotNone(serializer.fields.get("device"))

    def test_api_device_data_serializer_message_accepts_dict_obj(self):
        device_data = dict(
            message={"foo": "bar"},
        )
        serializer = DeviceDataSerializer(data=device_data)
        is_valid = serializer.is_valid()

        self.assertEqual(is_valid, True)
        self.assertIn("message", serializer.validated_data)
        self.assertEqual(serializer.validated_data["message"], device_data["message"])

    def test_api_device_data_serializer_message_accepts_json_obj(self):
        device_data = dict(
            message=json.loads('{"foo": "bar"}'),
        )
        serializer = DeviceDataSerializer(data=device_data)
        is_valid = serializer.is_valid()

        self.assertEqual(is_valid, True)
        self.assertIn("message", serializer.validated_data)
        self.assertEqual(serializer.validated_data["message"], device_data["message"])

    def test_api_device_data_serializer_message_accepts_json_string(self):
        device_data = dict(
            message='{"foo": "bar"}',
        )
        serializer = DeviceDataSerializer(data=device_data)
        is_valid = serializer.is_valid()

        self.assertEqual(is_valid, True)
        self.assertIn("message", serializer.validated_data)
        self.assertEqual(
            serializer.validated_data["message"], json.loads(device_data["message"])
        )

    def test_api_device_data_serializer_message_accepts_empty_dict(self):
        device_data = dict(
            message=dict(),
        )
        serializer = DeviceDataSerializer(data=device_data)
        is_valid = serializer.is_valid()

        self.assertEqual(is_valid, True)
        self.assertIn("message", serializer.validated_data)
        self.assertEqual(serializer.validated_data["message"], dict())

    def test_api_device_data_serializer_invalid_message_json_string(self):
        device_data = dict(
            message='{"foo": "bar"',
        )
        serializer = DeviceDataSerializer(data=device_data)
        is_valid = serializer.is_valid()

        self.assertEqual(is_valid, False)
        self.assertIn("message", serializer.errors)
        self.assertEqual(serializer.errors["message"][0].code, "invalid_json")
        self.assertEqual(
            serializer.errors["message"][0],
            "Message must be either a valid JSON object or a UTF-8 encoded JSON string.",
        )

    def test_api_device_data_serializer_invalid_message_empty_string(self):
        device_data = dict(
            message="",
        )
        serializer = DeviceDataSerializer(data=device_data)
        is_valid = serializer.is_valid()

        self.assertEqual(is_valid, False)
        self.assertIn("message", serializer.errors)
        self.assertEqual(serializer.errors["message"][0].code, "invalid_json")
        self.assertEqual(
            serializer.errors["message"][0],
            "Message must be either a valid JSON object or a UTF-8 encoded JSON string.",
        )

    def test_api_device_data_serializer_invalid_date(self):
        data_with_invalid_date = self.data.copy()
        data_with_invalid_date["date"] = "invalid date"
        serializer = DeviceDataSerializer(data=data_with_invalid_date)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("date", serializer.errors)

    def test_api_device_data_serializer_future_date(self):
        data_with_future_date = self.data.copy()
        data_with_future_date["date"] = timezone.now() + timezone.timedelta(days=1)
        serializer = DeviceDataSerializer(data=data_with_future_date)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("date", serializer.errors)

    def test_api_device_data_serializer_date_default_value(self):
        device_with_no_date = self.data.copy()
        device_with_no_date.pop("date", None)
        serializer = DeviceDataSerializer(data=device_with_no_date)
        is_valid = serializer.is_valid()
        date = serializer.validated_data.get("date", None)

        self.assertTrue(is_valid)
        self.assertIsNone(date)

    def test_api_device_data_serializer_create(self):
        new_data = self.data.copy()

        serializer = DeviceDataSerializer(
            data=new_data, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        new_device_data = serializer.save(
            device=self.first_device, date=new_data["date"]
        )

        self.assertEqual(is_valid, True)
        self.assertEqual(new_device_data.message, new_data["message"])
        self.assertEqual(new_device_data.device, self.first_device)
        self.assertEqual(new_device_data.date, new_data["date"])

    def test_api_device_data_serializer_create_date_is_optional(self):
        new_data = self.data.copy()
        new_data.pop("date", None)

        serializer = DeviceDataSerializer(
            data=new_data, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        new_device_data = serializer.save(device=self.first_device)

        self.assertEqual(is_valid, True)
        self.assertEqual(new_device_data.message, new_data["message"])
        self.assertEqual(new_device_data.device, self.first_device)

    def test_api_device_data_serializer_create_min_data(self):
        min_data = dict(message={"foo": "bar"})

        serializer = DeviceDataSerializer(
            data=min_data, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        new_device_data = serializer.save(device=self.first_device)

        self.assertEqual(is_valid, True)
        self.assertEqual(new_device_data.message, min_data["message"])
        self.assertEqual(new_device_data.device, self.first_device)


class TestDeviceDataAPIViewList(BaseDeviceDataAPIViewListTestCase):
    def test_api_data_list_anonymous_user(self):
        self.client.logout()
        response = self.client.get(
            self.url,
            follow=True,
        )
        error = response.data["detail"]

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(error, "Authentication credentials were not provided.")
        self.assertEqual(error.code, "not_authenticated")

    def test_api_data_list_get_device_data(self):
        response = self.client.get(self.url, data=dict(format="json"), follow=True)

        self.assertEqual(response.status_code, 200)
        for index, data in enumerate(
            self.first_device.devicedata_set.all().order_by("id"), start=0
        ):
            self.assertEqual(response.data[index]["id"], data.id)
            self.assertEqual(response.data[index]["message"], data.message)

    def test_api_data_list_create_device_data(self):
        new_data = self.data.copy()
        data_count_before = self.first_device.devicedata_set.count()
        response = self.client.post(
            self.url,
            data=new_data,
            format="json",
            follow=True,
        )
        data_count_after = self.first_device.devicedata_set.count()
        last_device_data = DeviceDataSerializer(
            instance=DeviceData.objects.last(),
            context={"request": response.wsgi_request},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data_count_before + 1, data_count_after)
        self.assertEqual(response.data["id"], last_device_data["id"].value)
        self.assertEqual(response.data["message"], last_device_data["message"].value)
        self.assertEqual(response.data["date"], last_device_data["date"].value)
        self.assertEqual(response.data["device"], last_device_data["device"].value)

    def test_api_data_list_create_device_min_data(self):
        min_data = dict(message={"foo": "bar"})
        data_count_before = self.first_device.devicedata_set.count()
        response = self.client.post(
            self.url,
            data=min_data,
            format="json",
            follow=True,
        )
        data_count_after = self.first_device.devicedata_set.count()
        last_device_data = DeviceDataSerializer(
            instance=DeviceData.objects.last(),
            context={"request": response.wsgi_request},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data_count_before + 1, data_count_after)
        self.assertEqual(response.data["id"], last_device_data["id"].value)
        self.assertEqual(response.data["message"], last_device_data["message"].value)
        self.assertEqual(response.data["date"], last_device_data["date"].value)
        self.assertEqual(response.data["device"], last_device_data["device"].value)

    def test_api_data_list_invalid_message_format_is_400(self):
        min_data = dict(
            message='{"foo": "bar"',
        )
        data_count_before = self.first_device.devicedata_set.count()
        response = self.client.post(
            self.url,
            data=min_data,
            format="json",
            follow=True,
        )
        data_count_after = self.first_device.devicedata_set.count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data_count_before, data_count_after)
        self.assertEqual(response.data["message"][0].code, "invalid_json")
        self.assertEqual(
            response.data["message"][0],
            "Message must be either a valid JSON object or a UTF-8 encoded JSON string.",
        )

    def test_api_data_list_creation_time_is_optional(self):
        new_device_data = self.data.copy()
        new_device_data.pop("date", None)

        device_count_before = self.first_device.devicedata_set.count()
        response = self.client.post(
            self.url,
            data=new_device_data,
            format="json",
            follow=True,
        )
        device_count_after = self.first_device.devicedata_set.count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(device_count_before + 1, device_count_after)

    def test_api_data_list_another_member_is_403(self):
        self.client.logout()
        self.client.force_login(self.second_member)

        response = self.client.get(
            self.url,
            format="json",
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_api_data_list_non_existing_user_is_403(self):
        response = self.client.get(
            path=reverse_lazy(
                "api:v1:data_list",
                kwargs=dict(
                    username="non_existing_member",
                    group_name=self.first_group.name,
                    device_uid=self.first_device.uid,
                ),
            ),
            follow=True,
        )

        # not logged in == permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_data_list_non_existing_device_group_is_404(self):
        response = self.client.get(
            path=reverse_lazy(
                "api:v1:data_list",
                kwargs=dict(
                    username=self.first_member.username,
                    group_name="non_existing_group",
                    device_uid=self.first_device.uid,
                ),
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_data_list_non_existing_device_is_404(self):
        response = self.client.get(
            path=reverse_lazy(
                "api:v1:data_list",
                kwargs=dict(
                    username=self.first_member.username,
                    group_name=self.first_group,
                    device_uid="00000000-0000-0000-0000-000000000000",
                ),
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestDeviceDataViewAPIDetails(BaseDeviceDataAPIViewDetailsTestCase):
    def test_api_device_data_details_get_data(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.first_serialized_data["id"].value)
        self.assertEqual(
            response.data["message"], self.first_serialized_data["message"].value
        )
        self.assertEqual(
            response.data["date"], self.first_serialized_data["date"].value
        )
        self.assertEqual(
            response.data["device"], self.first_serialized_data["device"].value
        )

    def test_api_device_data_details_non_existent_member_is_403(self):
        response = self.client.get(
            path=reverse_lazy(
                "api:v1:data_details",
                kwargs=dict(
                    username="non_existing_member",
                    group_name=self.first_group.name,
                    device_uid=self.first_device.uid,
                    data_id=1,
                ),
            ),
            follow=True,
        )

        # not logged in == permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_device_data_details_non_existent_device_group_is_404(self):
        response = self.client.get(
            path=reverse_lazy(
                "api:v1:data_details",
                kwargs=dict(
                    username=self.first_member.username,
                    group_name="non_existing_device_group",
                    device_uid=self.first_device.uid,
                    data_id=1,
                ),
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_device_data_details_non_existent_device_is_404(self):
        response = self.client.get(
            path=reverse_lazy(
                "api:v1:data_details",
                kwargs=dict(
                    username=self.first_member.username,
                    group_name=self.first_group.name,
                    device_uid="00000000-0000-0000-0000-000000000000",
                    data_id=1,
                ),
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_device_data_details_non_existent_device_data_is_404(self):
        response = self.client.get(
            path=reverse_lazy(
                "api:v1:data_details",
                kwargs=dict(
                    username=self.first_member.username,
                    group_name=self.first_group.name,
                    device_uid=self.first_device.uid,
                    data_id=99999,
                ),
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_device_data_details_another_member_device_is_403(self):
        self.client.logout()
        self.client.force_login(self.second_member)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_device_data_details_another_member_device_data_is_403(self):
        self.client.logout()
        self.client.force_login(self.second_member)

        response = self.client.get(
            path=reverse_lazy(
                "api:v1:data_details",
                kwargs=dict(
                    username=self.first_member.username,
                    group_name=self.first_group,
                    device_uid=self.first_device.uid,
                    data_id=self.first_device_data.id,
                ),
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_device_data_details_put_modify_device_data(self):
        new_message = dict(foo="bar", bar="baz")
        device_data = dict(
            message=new_message,
            device_uid=self.first_device_data.device.uid,
            date=self.first_device_data.date,
        )
        response = self.client.put(self.url, data=device_data, format="json")
        self.first_device_data.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.first_device_data.message, device_data["message"])
        self.assertEqual(self.first_device_data.date, device_data["date"])
        self.assertEqual(self.first_device_data.device.uid, device_data["device_uid"])

    def test_api_device_data_details_put_message_valid_json_string(self):
        data_message: str = json.dumps({"foo": "bar", "bar": "baz"})
        device_data = dict(
            message=data_message,
            device_uid=self.first_device_data.device.uid,
            date=self.first_device_data.date,
        )
        response = self.client.put(self.url, data=device_data, format="json")
        self.first_device_data.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.first_device_data.message, json.loads(data_message))

    def test_api_device_data_details_put_message_invalid_string_is_400(self):
        device_data = dict(
            message="bad_message",
            device_uid=self.first_device_data.device.uid,
            date=self.first_device_data.date,
        )
        response = self.client.put(self.url, data=device_data, format="json")
        self.first_device_data.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_device_data_details_patch_modify_device_data(self):
        new_message = dict(foo="bar", bar="baz")
        device_data = dict(message=new_message)
        response = self.client.patch(self.url, data=device_data, format="json")
        self.first_device_data.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.first_device_data.message, device_data["message"])

    def test_api_device_data_details_delete_remove_device_data(self):
        response = self.client.delete(
            self.url,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(DeviceData.DoesNotExist):
            self.first_device_data.refresh_from_db()
