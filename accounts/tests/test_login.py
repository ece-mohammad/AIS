from test.pages.common import HomePage, LogIn, MemberProfile
from test.utils.helpers import (client_login, page_in_response,
                                response_user_logged_in)
from typing import *

from django.test import TestCase

from accounts.models import Member

# Create your tests here.



TEST_USER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password= "testpassword",
)

TEST_USER_INVALID_PASSWORD: Final[Dict[str, str]] = dict(
    username="testuser",
    password= "wrong_password",
)

TEST_USER_INVALID_USERNAME: Final[Dict[str, str]] = dict(
    username="wrong_username",
    password= "testpassword",
)

INVALID_CREDENTIALS_MESSAGE: Final[str] = "Please enter a correct username and password. Note that both fields may be case-sensitive."


class BaseLoginTestCase(TestCase):
    def setUp(self) -> None:
        member = Member.objects.create(username=TEST_USER_CREDENTIALS["username"])
        member.set_password(TEST_USER_CREDENTIALS["password"])
        member.save()
        
        return super().setUp()


class TestLoginPageRendering(BaseLoginTestCase):
    def test_login_page_rendering(self):
        """Test that login page renders correctly"""
        response = self.client.get(LogIn.get_url())
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(page_in_response(LogIn, response)[0])


class TestLoginForm(BaseLoginTestCase):
    def setUp(self) -> None:
        self.response = self.client.get(LogIn.get_url())
        self.form = self.response.context.get("form")
        self.username_filed = self.form.fields.get("username", None)
        self.password_filed = self.form.fields.get("password", None)
        return super().setUp()
    
    
    def test_login_form_fields(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(len(self.form.fields), 2)
        self.assertIsNotNone(self.username_filed)
        self.assertIsNotNone(self.password_filed)
    
    def test_login_form_fields_username(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.username_filed.label, "Username")
        self.assertEqual(self.username_filed.required, True)
        self.assertEqual(self.username_filed.initial, None)
    
    def test_login_form_fields_password(self):        
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.password_filed.label, "Password")
        self.assertEqual(self.password_filed.required, True)
        self.assertEqual(self.password_filed.initial, None)


class TestLoginView(BaseLoginTestCase):
    def test_login_valid_user_credentials(self):
        response = client_login(self.client, TEST_USER_CREDENTIALS)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_user_logged_in(response))
        
    def test_login_invalid_username(self):
        response = client_login(self.client, TEST_USER_INVALID_USERNAME)
        
        form = response.context.get("form")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.errors), 1)
        self.assertFormError(form, "username", [])
        self.assertFormError(form, "password", [])
        self.assertEqual(form.errors["__all__"], [INVALID_CREDENTIALS_MESSAGE])
        self.assertContains(response, INVALID_CREDENTIALS_MESSAGE)
        self.assertFalse(response_user_logged_in(response))
        
    def test_login_invalid_password(self):
        response = client_login(self.client, TEST_USER_INVALID_PASSWORD)
        
        form = response.context.get("form")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.errors), 1)
        self.assertFormError(form, "username", [])
        self.assertFormError(form, "password", [])
        self.assertEqual(form.errors["__all__"], [INVALID_CREDENTIALS_MESSAGE])
        self.assertContains(response, INVALID_CREDENTIALS_MESSAGE)
        self.assertFalse(response_user_logged_in(response))
    
    def test_login_anonymous_user(self):
        response = self.client.get(
            LogIn.get_url(),
        )
        
        is_login_page = page_in_response(page=LogIn, response=response)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(is_login_page[0])
        
    def test_login_member_redirects_to_homepage(self):
        client_login(self.client, TEST_USER_CREDENTIALS)
        response = self.client.get(
            LogIn.get_url(),
            follow=True
        )
        
        self.assertRedirects(response, HomePage.get_url(), status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_login_redirects_to_next_page(self):
        next_page = MemberProfile.get_url(username=TEST_USER_CREDENTIALS["username"])
        next_url = f"{LogIn.get_url()}?next={next_page}"
        response = self.client.post(
            next_url,
            TEST_USER_CREDENTIALS,
            follow=True,
        )
        self.assertRedirects(response, next_page, status_code=302, target_status_code=200, fetch_redirect_response=True)
