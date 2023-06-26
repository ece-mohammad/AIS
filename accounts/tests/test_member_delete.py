from test.pages.common import HomePage, MemberDelete, LogIn
from test.utils.helpers import client_login, create_member, page_in_response
from typing import *

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.test.client import Client

from accounts.models import Member

TEST_MEMBER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password="testpassword",
)


class TestAccountDelete(TestCase):
    def setUp(self):
        self.member = create_member(**TEST_MEMBER_CREDENTIALS)
        self.client = Client()
        client_login(self.client, TEST_MEMBER_CREDENTIALS)
        super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_member_delete_rendering(self):
        response = self.client.get(MemberDelete.get_url(username=self.member.username))
        
        is_delete_page = page_in_response(MemberDelete, response)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(is_delete_page[0])
    
    def test_member_delete_form_password_required(self):
        response = self.client.post(
            MemberDelete.get_url(username=self.member.username),
            {"password": ""},
            follow=False
        )
        
        self.assertEqual(response.status_code, 200)
        
        form = response.context.get("form")
        self.assertEqual(form.errors["password"], ["This field is required."])
        

    def test_member_delete_form_password_invalid(self):
        response = self.client.post(
            MemberDelete.get_url(username=self.member.username),
            {"password": "invalid_password"},
            follow=False
        )
        
        self.assertEqual(response.status_code, 200)
        
        form = response.context.get("form")
        self.assertEqual(form.errors["password"], ["The password is incorrect"])
        
    
    def test_member_delete_redirects_anonymous_user(self):
        client = Client()
        response = client.get(
            MemberDelete.get_url(username=self.member.username),
            follow=True,
        )
        
        next_url = f"{LogIn.get_url()}?next={MemberDelete.get_url(username=self.member.username)}"        
        self.assertRedirects(response, next_url)
    
    def test_member_delete_wrong_user_forbidden(self):
        response = self.client.get(
            MemberDelete.get_url(username="wrong_user"),
            follow=True,
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_member_delete_sequence(self):
        response = self.client.post(
            MemberDelete.get_url(username=self.member.username),
            data={"password": TEST_MEMBER_CREDENTIALS["password"]},
            follow=True,
        )
        
        self.assertRedirects(response, HomePage.get_url())
        with self.assertRaises(ObjectDoesNotExist):
            Member.objects.get(username=self.member.username)
