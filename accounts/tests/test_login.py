""" 
Test user login view

"""
from typing import *
from urllib.parse import urljoin, urlunparse, urlparse

from django.test import TestCase
from django.test.client import Client

from accounts.models import Member
from test.pages.common import HomePage, LogIn, PasswordChange
from test.utils.helpers import (client_login, is_redirection_target,
                                    page_in_response, response_user_logged_in)

# Create your tests here.



TEST_USER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password= "testpassword",
)

TEST_USER_INVALID_PASSWORD: Final[Dict[str, str]] = dict(
    username="testuser",
    password= "wrongpassword",
)

TEST_USER_INVALID_USERNAME: Final[Dict[str, str]] = dict(
    username="wrongusername",
    password= "testpassword",
)

INVALID_CREDENTIALS_MESSAGE: Final[str] = "Please enter a correct username and password. Note that both fields may be case-sensitive."


class TestLogin(TestCase):
    
    def setUp(self) -> None:
        # set up member
        member = Member.objects.create(
            username=TEST_USER_CREDENTIALS["username"],
        )
        member.set_password(TEST_USER_CREDENTIALS["password"])
        member.save()
        
        # set up client
        self.client = Client()
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    
    def test_login_page_rendering(self):
        """Test that login page renders correctly"""
        response = self.client.get(LogIn.url)
        
        self.assertTemplateUsed(response, LogIn.template_name)
        self.assertEqual(response.resolver_match.view_name, LogIn.view_name)
    
    def test_login_valid_user_credentials(self):
        response = client_login(self.client, TEST_USER_CREDENTIALS)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_user_logged_in(response))
        
        
    def test_login_invalid_username(self):
        response = client_login(self.client, TEST_USER_INVALID_USERNAME)
        
        is_login_page = page_in_response(page=LogIn, response=response)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, INVALID_CREDENTIALS_MESSAGE)
        self.assertTrue(is_login_page[0])
        self.assertFalse(response_user_logged_in(response))
        
    def test_login_invalid_password(self):
        response = client_login(self.client, TEST_USER_INVALID_PASSWORD)
        
        is_login_page = page_in_response(page=LogIn, response=response)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, INVALID_CREDENTIALS_MESSAGE)
        self.assertTrue(is_login_page[0])
        self.assertFalse(response_user_logged_in(response))
    
    def test_login_anonymous_user(self):
        response = self.client.get(
            LogIn.url,
        )
        
        is_login_page = page_in_response(page=LogIn, response=response)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(is_login_page[0])
        
    def test_login_member_redirects_to_homepage(self):
        client_login(self.client, TEST_USER_CREDENTIALS)
        
        response = self.client.get(
            LogIn.url,
            follow=True
        )
        
        self.assertRedirects(response, HomePage.url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTrue(is_redirection_target(HomePage, response))

    def test_login_redirects_to_next_page(self):
        next_page = "/accounts/profile/testuser/"
        response = self.client.post(
            f"{LogIn.url}?next={next_page}",
            TEST_USER_CREDENTIALS,
            follow=True,
        )
        
        self.assertRedirects(response, next_page, status_code=302, target_status_code=200, fetch_redirect_response=True)

