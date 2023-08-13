from test.pages.common import LogIn, MemberProfile
from test.utils.helpers import client_login, create_member
from typing import *

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse_lazy

MEMBER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="test_member",
    password="test_password",
)


class TestMemberOwnProfileView(TestCase):
    def setUp(self) -> None:
        self.my_profile_url = reverse_lazy("accounts:my_profile")
        self.member = create_member(**MEMBER_CREDENTIALS)
        client_login(self.client, MEMBER_CREDENTIALS)
        return super().setUp()

    def test_member_own_profile_view_redirects_anon_user(self):
        client = Client()
        response = client.get(
            self.my_profile_url,
            follow=True,
        )
        next_url = f"{LogIn.get_url()}?next={self.my_profile_url}"

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, next_url, 302, 200, fetch_redirect_response=True)

    def test_member_own_profile_redirects_to_member_profile(self):
        response = self.client.get(
            self.my_profile_url,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            MemberProfile.get_url(username=self.member.username),
            302,
            200,
            fetch_redirect_response=True,
        )
