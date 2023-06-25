from typing import *
from urllib.parse import urljoin

from django.test.client import Client
from django.test import TestCase
from django.core.exceptions import PermissionDenied

from test.pages.common import HomePage, LogOut, SignUp, LogIn, MemberDeactivate
from test.utils.helpers import create_member, client_login, client_logout, page_in_response
from accounts.models import Member


FIRST_MEMBER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="first_test_user",
    password="test_password",
)

SECOND_MEMBER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="second_test_user",
    password="test_password",
)


class MemberDeactivateTest(TestCase):
    def get_deactivate_url(self, username: str = "") -> str:
        if not username:
            username = FIRST_MEMBER_CREDENTIALS['username']    
        return f"{urljoin(MemberDeactivate.raw_url, username)}/"
    
    def setUp(self):
        self.first_member = create_member(**FIRST_MEMBER_CREDENTIALS)
        self.second_member = create_member(**SECOND_MEMBER_CREDENTIALS)
        self.deactivate_url = self.get_deactivate_url(FIRST_MEMBER_CREDENTIALS["username"])
        
        self.client = Client()
        client_login(self.client, FIRST_MEMBER_CREDENTIALS)
        
        return super().setUp()
    
    def tearDown(self):
        client_logout(self.client)
        return super().tearDown()
    
    def test_member_deactivate_page_rendering(self):
        response = self.client.get(self.deactivate_url)
        
        self.assertEqual(200, response.status_code)
        self.assertTrue(page_in_response(MemberDeactivate, response)[0])
        
    def test_member_deactivate_form_invalid_password(self):
        response = self.client.post(
            self.deactivate_url,
            {"password": f"invalid_{FIRST_MEMBER_CREDENTIALS['password']}"}
        )
        
        form = response.context["form"]
        
        self.assertEqual(200, response.status_code)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        
    def test_member_deactivate_redirects_anonymous_user(self):
        client = Client()
        response = client.get(self.deactivate_url, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, LogIn.title)
        
    def test_member_deactivate_another_member_is_forbidden(self):
        response = self.client.get(
            self.get_deactivate_url(SECOND_MEMBER_CREDENTIALS["username"]),
            follow=False
        )
        
        self.assertEqual(403, response.status_code)
        
    def test_member_deactivate_sequence(self):
        response = self.client.post(
            self.deactivate_url,
            {"password": FIRST_MEMBER_CREDENTIALS["password"]},
            follow=True
        )
        
        self.assertEqual(200, response.status_code)
        self.assertRedirects(response, HomePage.url)
        member = Member.objects.get(username=FIRST_MEMBER_CREDENTIALS["username"])
        self.assertFalse(member.is_active)
    
    def test_member_deactivate_keeps_old_password(self):
        response = self.client.post(
            self.deactivate_url,
            {"password": FIRST_MEMBER_CREDENTIALS["password"]},
            follow=True
        )
        
        member = Member.objects.get(username=FIRST_MEMBER_CREDENTIALS["username"])
        self.assertFalse(member.is_active)
        self.assertTrue(member.check_password(FIRST_MEMBER_CREDENTIALS["password"]))

