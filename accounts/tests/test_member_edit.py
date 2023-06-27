from typing import *

from django.test.client import Client
from django.test import TestCase

from test.pages.common import  MemberEdit, HomePage, LogIn, MemberProfile
from test.utils.helpers import create_member, client_login, page_in_response


MEMBER_USERNAME : Final[str] = "member"
MEMBER_EMAIL : Final[str] = "member@email.com"
MEMBER_FIRST_NAME : Final[str] = "Test"
MEMBER_LAST_NAME : Final[str] = "Member"

MEMBER_NEW_USERNAME : Final[str] = "member_new"
MEMBER_NEW_EMAIL: Final[str] = "new_member@email.com"
MEMBER_NEW_FIRST_NAME: Final[str] = "New Test"
MEMBER_NEW_LAST_NAME: Final[str] = "New Member"

MEMBER_DATA: Final[Dict[str, str]] = dict(
    username=MEMBER_USERNAME,
    email=MEMBER_EMAIL,
    password="test_password",
    first_name=MEMBER_FIRST_NAME,
    last_name=MEMBER_LAST_NAME,
)

class TestMemberEdit(TestCase):
    def setUp(self) -> None:
        self.member = create_member(**MEMBER_DATA)
        self.client = Client()
        client_login(self.client, MEMBER_DATA)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_member_edit_rendering(self):
        response = self.client.get(
            MemberEdit.get_url(username=self.member.username)
        )
        self.assertEqual(response.status_code, 200)
        
        member_edit = page_in_response(MemberEdit, response)
        self.assertTrue(member_edit[0])
    
    def test_member_redirects_anonymous_user(self):
        client = Client()
        response = client.get(
            MemberEdit.get_url(username=self.member.username),
            follow=True
        )
        
        next_url = f"{LogIn.get_url()}?next={MemberEdit.get_url(username=self.member.username)}"
        
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, next_url, 302, 200, fetch_redirect_response=True)
        
    def test_member_edit_another_user_forbidden(self):
        response = self.client.get(
            MemberEdit.get_url(username="another_user"),
            follow=True
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_member_edit_username_required(self):
        response = self.client.post(
            MemberEdit.get_url(username=self.member.username),
            data=dict(
                username="",
                first_name=MEMBER_NEW_FIRST_NAME,
                last_name=MEMBER_NEW_LAST_NAME,
                email=MEMBER_NEW_EMAIL,
            ),
            follow=True,
        )        
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context.get("form"), "username", ["This field is required."])
        self.assertContains(response, "This field is required.")
        
    def test_member_edit_fields_not_required(self):
        response = self.client.post(
            MemberEdit.get_url(username=self.member.username),
            data=dict(
                username=MEMBER_NEW_USERNAME,
                first_name="",
                last_name="",
                email="",
            ),
            follow=True,
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, MemberProfile.get_url(username=MEMBER_NEW_USERNAME))
        
        self.member.refresh_from_db()
        self.assertEqual(self.member.username, MEMBER_NEW_USERNAME)
        self.assertEqual(self.member.first_name, "")
        self.assertEqual(self.member.last_name, "")
        self.assertEqual(self.member.email, "")
    
    def test_member_edit_accepts_unique_case_insensitive(self):
        response = self.client.post(
            MemberEdit.get_url(username=self.member.username),
            data=dict(
                username=MEMBER_USERNAME.capitalize(),
                first_name=MEMBER_NEW_FIRST_NAME,
                last_name=MEMBER_NEW_LAST_NAME,
                email=MEMBER_NEW_EMAIL,
            ),
            follow=True,
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context.get("form"), "username", ["A user with that username already exists."])
        self.assertContains(response, "A user with that username already exists.")
        
    def test_member_edit_accepts_unchanged_username(self):
        response = self.client.post(
            MemberEdit.get_url(username=self.member.username),
            data=dict(
                username=MEMBER_USERNAME,
                first_name=MEMBER_NEW_FIRST_NAME,
                last_name=MEMBER_NEW_LAST_NAME,
                email=MEMBER_NEW_EMAIL,
            ),
            follow=True,
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, MemberProfile.get_url(username=MEMBER_USERNAME), 302, 200, fetch_redirect_response=True)
    
    def test_member_edit_sequence(self):
        response = self.client.post(
            MemberEdit.get_url(username=self.member.username),
            data=dict(
                username=MEMBER_NEW_USERNAME,
                first_name=MEMBER_NEW_FIRST_NAME,
                last_name=MEMBER_NEW_LAST_NAME,
                email=MEMBER_NEW_EMAIL,
            ),
            follow=True,
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, MemberProfile.get_url(username=MEMBER_NEW_USERNAME))
        
        self.member.refresh_from_db()
        self.assertEqual(self.member.username, MEMBER_NEW_USERNAME)
        self.assertEqual(self.member.email, MEMBER_NEW_EMAIL)
        self.assertEqual(self.member.first_name, MEMBER_NEW_FIRST_NAME)
        self.assertEqual(self.member.last_name, MEMBER_NEW_LAST_NAME)
