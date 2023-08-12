from typing import *

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from accounts.models import Member
from api.v1.serializers import MemberHyperlinkField, MemberSerializer


# -----------------------------------------------------------------------------
# Base Test classes (common set ups)
# -----------------------------------------------------------------------------
class BaseMembersAPIViewDetailsTestCase(APITestCase):
    fixtures = ["api/test_fixture.json"]

    def setUp(self):
        self.first_member = Member.objects.first()
        self.second_member = Member.objects.filter(
            Q(is_active=True) & ~Q(id=self.first_member.id)
        ).first()
        self.inactive_member = Member.objects.filter(is_active=False).first()
        self.request = APIRequestFactory().get("/")
        self.request.user = self.first_member
        self.client.force_login(self.first_member)
        return super().setUp()


# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------
class TestMembersHyperlinkField(BaseMembersAPIViewDetailsTestCase):
    def setUp(self):
        ret = super().setUp()
        self.url_field = MemberHyperlinkField()
        self.view_name = "api:v1:member_details"
        self.lookup_field = "username"
        self.lookup_url_kwarg = "username"
        self.url = reverse_lazy(
            self.view_name,
            kwargs={
                self.lookup_url_kwarg: getattr(self.first_member, self.lookup_field)
            },
        )
        response = self.client.get(self.url)
        self.request = response.wsgi_request
        return ret

    def test_member_hyperlink_field_assert(self):
        self.url_field.assert_member_link_field(
            self.first_member, self.view_name, self.lookup_field, self.lookup_url_kwarg
        )

    def test_member_hyperlink_field_assert_invalid(self):
        with self.assertRaises(ValueError):
            self.url_field.assert_member_link_field(
                AnonymousUser, self.view_name, self.lookup_field, self.lookup_url_kwarg
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_member_link_field(
                self.first_member,
                "invalid_view_name",
                self.lookup_field,
                self.lookup_url_kwarg,
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_member_link_field(
                self.first_member,
                self.view_name,
                "invalid_lookup_field",
                self.lookup_url_kwarg,
            )

        with self.assertRaises(ValueError):
            self.url_field.assert_member_link_field(
                self.first_member,
                self.view_name,
                self.lookup_field,
                "invalid_lookup_url_kwarg",
            )

    def test_member_hyperlink_field_url_kwargs_from_instance(self):
        url_kwargs = self.url_field.get_member_url_kwargs_from_instance(
            self.first_member
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_member, self.lookup_field),
        )

    def test_member_hyperlink_field_url_kwargs_from_request(self):
        url_kwargs = self.url_field.get_member_url_kwargs_from_request(self.request)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_member, self.lookup_field),
        )

    def test_member_hyperlink_field_url_kwargs(self):
        url_kwargs = self.url_field.get_member_url_kwargs(
            self.first_member, self.request
        )

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_member, self.lookup_field),
        )

    def test_member_hyperlink_field_url_kwargs_none_instance(self):
        url_kwargs = self.url_field.get_member_url_kwargs(None, self.request)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_member, self.lookup_field),
        )

    def test_member_hyperlink_field_url_kwargs_none_request(self):
        url_kwargs = self.url_field.get_member_url_kwargs(self.first_member, None)

        self.assertIn(self.lookup_url_kwarg, url_kwargs)
        self.assertEqual(
            url_kwargs.get(self.lookup_url_kwarg),
            getattr(self.first_member, self.lookup_field),
        )

    def test_member_hyperlink_field_url_kwargs_none_instance_and_request(self):
        with self.assertRaises(AttributeError):
            self.url_field.get_member_url_kwargs(None, None)


class TestMembersAPISerializer(BaseMembersAPIViewDetailsTestCase):
    def test_api_members_serializer_fields(self):
        serializer = MemberSerializer()

        self.assertIsNotNone(serializer.fields.get("url"))
        self.assertIsNotNone(serializer.fields.get("id"))
        self.assertIsNotNone(serializer.fields.get("username"))
        self.assertIsNotNone(serializer.fields.get("first_name"))
        self.assertIsNotNone(serializer.fields.get("last_name"))
        self.assertIsNotNone(serializer.fields.get("email"))
        self.assertIsNotNone(serializer.fields.get("date_joined"))
        self.assertIsNotNone(serializer.fields.get("is_active"))
        self.assertIsNotNone(serializer.fields.get("is_staff"))
        self.assertIsNotNone(serializer.fields.get("devicegroup_set"))

    def test_api_members_serializer_data(self):
        serializer = MemberSerializer(
            instance=self.first_member, context={"request": self.request}
        )
        data = serializer.data.copy()

        self.assertEqual(data.get("id"), self.first_member.id)
        self.assertEqual(data.get("username"), self.first_member.username)
        self.assertEqual(data.get("first_name"), self.first_member.first_name)
        self.assertEqual(data.get("last_name"), self.first_member.last_name)
        self.assertEqual(data.get("email"), self.first_member.email)
        self.assertEqual(data.get("is_active"), self.first_member.is_active)
        self.assertEqual(data.get("is_staff"), self.first_member.is_staff)
        self.assertEqual(
            len(data.get("devicegroup_set")), self.first_member.devicegroup_set.count()
        )


class TestMembersAPIViewDetails(BaseMembersAPIViewDetailsTestCase):
    def test_api_members_details_get(self):
        response = self.client.get(
            reverse_lazy(
                "api:v1:member_details", kwargs={"username": self.first_member.username}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), self.first_member.id)
        self.assertEqual(response.data.get("username"), self.first_member.username)
        self.assertEqual(response.data.get("first_name"), self.first_member.first_name)
        self.assertEqual(response.data.get("last_name"), self.first_member.last_name)
        self.assertEqual(response.data.get("email"), self.first_member.email)
        self.assertEqual(response.data.get("is_active"), self.first_member.is_active)
        self.assertEqual(response.data.get("is_staff"), self.first_member.is_staff)
        self.assertEqual(
            len(response.data.get("devicegroup_set")),
            self.first_member.devicegroup_set.count(),
        )

    def test_api_members_details_post_is_not_allowed(self):
        response = self.client.post(
            reverse_lazy(
                "api:v1:member_details", kwargs={"username": self.first_member.username}
            ),
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_members_details_put_is_not_allowed(self):
        response = self.client.put(
            reverse_lazy(
                "api:v1:member_details", kwargs={"username": self.first_member.username}
            ),
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_members_details_patch_is_not_allowed(self):
        response = self.client.patch(
            reverse_lazy(
                "api:v1:member_details", kwargs={"username": self.first_member.username}
            ),
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_members_details_delete_is_not_allowed(self):
        response = self.client.delete(
            reverse_lazy(
                "api:v1:member_details", kwargs={"username": self.first_member.username}
            ),
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_members_details_get_another_member_is_403(self):
        response = self.client.get(
            reverse_lazy(
                "api:v1:member_details",
                kwargs={"username": self.second_member.username},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get("detail"),
            "You do not have permission to perform this action.",
        )

    def test_api_members_details_post_anonymous_user(self):
        self.client.logout()
        response = self.client.get(
            reverse_lazy(
                "api:v1:member_details", kwargs={"username": self.first_member.username}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_members_details_post_inactive_member(self):
        self.client.logout()
        self.client.force_login(self.inactive_member)
        response = self.client.get(
            reverse_lazy(
                "api:v1:member_details",
                kwargs={"username": self.inactive_member.username},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get("detail"), "Authentication credentials were not provided."
        )
