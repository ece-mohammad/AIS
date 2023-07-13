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


class BaseMemberDeleteTestCase(TestCase):
    def setUp(self):
        self.member = create_member(**TEST_MEMBER_CREDENTIALS)
        client_login(self.client, TEST_MEMBER_CREDENTIALS)
        super().setUp()


class TestMemberDeleteRendering(BaseMemberDeleteTestCase):
    def test_member_delete_rendering(self):
        response = self.client.get(MemberDelete.get_url(username=self.member.username))
        is_delete_page = page_in_response(MemberDelete, response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(is_delete_page[0])


class TestMemberDeleteForm(BaseMemberDeleteTestCase):
    def test_member_delete_form_fields(self):
        response = self.client.get(
            MemberDelete.get_url(username=self.member.username),
            follow=True
        )
        form = response.context.get("form")
        password_field = form.fields.get("password")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.fields), 1)
        self.assertEqual(password_field.label, "Password")
        self.assertEqual(password_field.required, True)
        self.assertEqual(password_field.initial, None)


class TestMemberDeleteView(BaseMemberDeleteTestCase):
    def test_member_delete_password_empty(self):
        response = self.client.post(
            MemberDelete.get_url(username=self.member.username),
            {"password": ""},
            follow=True
        )
        form = response.context.get("form")
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(form, "password", ["This field is required."])
        self.assertContains(response, "This field is required.")
        
    def test_member_delete_form_password_invalid(self):
        response = self.client.post(
            MemberDelete.get_url(username=self.member.username),
            {"password": "invalid_password"},
            follow=False
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context.get("form"), "password", ["The password is incorrect"])
        self.assertContains(response, "The password is incorrect")
        
    
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
