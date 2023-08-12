from test.pages.common import DeviceSearch, LogIn
from test.utils.helpers import (
    client_login,
    client_logout,
    create_member,
    page_in_response,
)
from typing import *

from django.conf import settings
from django.test import TestCase

from devices.models import Device

SEARCH_RESULTS_PER_PAGE: Final[int] = settings.PAGINATION_SIZE

FIRST_MEMBER: Final[Dict[str, str]] = dict(
    username="first_member",
    password="test_password",
)

FIRST_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="first_device_group",
    description="first device group description",
)

FIRST_DEVICE_NAME: Final[str] = "first_device"
SECOND_DEVICE_NAME: Final[str] = "second_device"

SECOND_MEMBER: Final[Dict[str, str]] = dict(
    username="second_member",
    password="test_password",
)

SECOND_DEVICE_GROUP: Final[Dict[str, str]] = dict(
    name="second_device_group",
    description="first device group description",
)

THIRD_DEVICE_NAME: Final[str] = "third_device"


class BaseDeviceSearchTestCase(TestCase):
    def setUp(self) -> None:
        self.first_member = create_member(**FIRST_MEMBER)
        self.first_device_group = self.first_member.devicegroup_set.create(
            **FIRST_DEVICE_GROUP
        )
        self.first_device = self.first_device_group.device_set.create(
            name=FIRST_DEVICE_NAME,
            uid=Device.generate_device_uid(
                f"{self.first_member.username}-{self.first_device_group.name}-{FIRST_DEVICE_NAME}"
            ),
        )

        self.second_device = self.first_device_group.device_set.create(
            name=SECOND_DEVICE_NAME,
            uid=Device.generate_device_uid(
                f"{self.first_member.username}-{self.first_device_group.name}-{SECOND_DEVICE_NAME}"
            ),
        )

        self.second_member = create_member(**SECOND_MEMBER)
        self.second_device_group = self.second_member.devicegroup_set.create(
            **SECOND_DEVICE_GROUP
        )
        self.third_device = self.second_device_group.device_set.create(
            name=THIRD_DEVICE_NAME,
            uid=Device.generate_device_uid(
                f"{self.second_member.username}-{self.second_device_group.name}-{SECOND_DEVICE_NAME}"
            ),
        )

        client_login(self.client, FIRST_MEMBER)
        return super().setUp()


class TestDeviceSearchRendering(BaseDeviceSearchTestCase):
    def setUp(self, **kwargs: Any) -> Any:
        ret = super().setUp()
        self.response = self.client.get(DeviceSearch.get_url())
        return ret

    def test_device_search_rendering(self) -> None:
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(page_in_response(DeviceSearch, self.response)[0])


class TestDeviceSearchForm(BaseDeviceSearchTestCase):
    def setUp(self) -> None:
        ret = super().setUp()
        self.response = self.client.get(DeviceSearch.get_url())
        self.form = self.response.context.get("form")
        return ret

    def test_device_search_form_fields(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertIsNotNone(self.form)
        self.assertEqual(len(self.form.fields), 2)
        self.assertIn("name", self.form.fields)
        self.assertIn("search_for", self.form.fields)

    def test_device_search_form_fields_name(self):
        self.name_field = self.form.fields.get("name")
        self.assertEqual(self.name_field.label, "Name")
        self.assertEqual(self.name_field.required, False)
        self.assertEqual(self.name_field.initial, None)

    def test_device_search_form_fields_search_for(self):
        self.search_field = self.form.fields.get("search_for")
        self.assertEqual(self.search_field.label, "Search For")
        self.assertEqual(self.search_field.required, False)
        self.assertEqual(self.search_field.initial, "device")


class TestDeviceSearchView(BaseDeviceSearchTestCase):
    def test_device_search_redirects_anonymous_user(self):
        client_logout(self.client)
        response = self.client.get(DeviceSearch.get_url())
        next_url = f"{LogIn.get_url()}?next={DeviceSearch.get_url()}"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

    def test_device_search_redirects_to_results_page(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name=self.first_device.name,
                search_for="device",
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(page_in_response(DeviceSearch, response)[0])

    def test_device_search_device_search_results(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name=self.first_device.name,
                search_for="device",
            ),
            follow=True,
        )
        context = response.context
        result_link = f'<a href="{self.first_device.get_absolute_url()}">{self.first_device.name}</a>'

        self.assertEqual(response.status_code, 200)
        self.assertIn("search_results", context.keys())
        self.assertContains(response, self.first_device.name)
        self.assertInHTML(result_link, response.content.decode())

    def test_device_search_case_insensitive(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name=self.first_device.name.upper(),
                search_for="device",
            ),
            follow=True,
        )
        context = response.context
        result_link = f'<a href="{self.first_device.get_absolute_url()}">{self.first_device.name}</a>'

        self.assertEqual(response.status_code, 200)
        self.assertIn("search_results", context.keys())
        self.assertContains(response, self.first_device.name)
        self.assertInHTML(result_link, response.content.decode())

    def test_device_search_partial_name(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name=self.first_device.name.split("_")[-1],
                search_for="device",
            ),
            follow=True,
        )
        context = response.context
        result_link = f'<a href="{self.first_device.get_absolute_url()}">{self.first_device.name}</a>'

        self.assertEqual(response.status_code, 200)
        self.assertIn("search_results", context.keys())
        self.assertContains(response, self.first_device.name)
        self.assertInHTML(result_link, response.content.decode())

    def test_device_search_own_devices(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name="device",
                search_for="device",
            ),
            follow=True,
        )
        context = response.context
        third_device_link = f'<a href="{self.third_device.get_absolute_url()}">{self.third_device.name}</a>'

        self.assertEqual(response.status_code, 200)
        self.assertIn("search_results", context.keys())
        self.assertNotContains(response, self.third_device.name)
        self.assertFalse(third_device_link in response.content.decode(response.charset))

    def test_device_search_own_groups(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name=self.first_device_group.name,
                search_for="group",
            ),
            follow=True,
        )
        group_link = f'<a href="{self.first_device_group.get_absolute_url()}">{self.first_device_group.name}</a>'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_device_group.name)
        self.assertInHTML(group_link, response.content.decode())

    def test_device_search_empty_results(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name="non_existent_device",
                search_for="device",
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results found")


class TestDeviceSearchPagination(BaseDeviceSearchTestCase):
    def setUp(self) -> None:
        ret = super().setUp()

        self.first_device_group.device_set.all().delete()
        for index in range(settings.PAGINATION_SIZE * 2):
            self.first_device_group.device_set.create(
                name=f"device_{index:02d}",
                uid=Device.generate_device_uid(
                    f"{self.first_member.username}-{self.first_device_group.name}-device_{index}"
                ),
            )

        return ret

    def test_device_search_pagination(self):
        first_page = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name="device",
                search_for="device",
                page=1,
            ),
            follow=True,
        )

        second_page = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name="device",
                search_for="device",
                page=2,
            ),
            follow=True,
        )

        first_context = first_page.context
        second_context = second_page.context

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(first_context.get("page_obj").number, 1)
        self.assertEqual(first_context.get("page_obj").paginator.num_pages, 2)
        self.assertEqual(
            first_context.get("page_obj").paginator.count, settings.PAGINATION_SIZE * 2
        )
        self.assertEqual(
            len(first_context.get("page_obj").object_list), settings.PAGINATION_SIZE
        )

        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(second_context.get("page_obj").number, 2)
        self.assertEqual(second_context.get("page_obj").paginator.num_pages, 2)
        self.assertEqual(
            second_context.get("page_obj").paginator.count, settings.PAGINATION_SIZE * 2
        )
        self.assertEqual(
            len(second_context.get("page_obj").object_list), settings.PAGINATION_SIZE
        )

        for device_index in range(SEARCH_RESULTS_PER_PAGE):
            device_name = f"device_{device_index:02d}"
            device_link = f'<a href="{self.first_device_group.device_set.get(name=device_name).get_absolute_url()}">{device_name}</a>'
            self.assertContains(first_page, device_name)
            self.assertInHTML(device_link, first_page.content.decode())

        for device_index in range(SEARCH_RESULTS_PER_PAGE, SEARCH_RESULTS_PER_PAGE * 2):
            device_name = f"device_{device_index:02d}"
            device_link = f'<a href="{self.first_device_group.device_set.get(name=device_name).get_absolute_url()}">{device_name}</a>'
            self.assertContains(second_page, device_name)
            self.assertInHTML(device_link, second_page.content.decode())

    def test_device_search_pagination_first_page(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name="device",
                search_for="device",
                page="first",
            ),
            follow=True,
        )
        context = response.context

        self.assertEqual(response.status_code, 200)
        self.assertEqual(context.get("page_obj").number, 1)

    def test_device_search_pagination_last_page(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name="device",
                search_for="device",
                page="last",
            ),
            follow=True,
        )

        context = response.context

        self.assertEqual(response.status_code, 200)
        self.assertEqual(context.get("page_obj").number, 2)

    def test_device_search_pagination_invalid_page_number_is_404(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name="device",
                search_for="device",
                page=3,
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 404)

    def test_device_search_pagination_invalid_page_name_is_404(self):
        response = self.client.get(
            DeviceSearch.get_url(),
            data=dict(
                name="device",
                search_for="device",
                page="invalid",
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 404)

    def test_device_search_post_method_is_not_allowed(self):
        response = self.client.post(
            DeviceSearch.get_url(),
            data=dict(name="device", search_for="device,"),
            follow=True,
        )

        self.assertEqual(response.status_code, 405)
