from django.test import TestCase
from django.test.client import Client
from django.http import HttpResponseRedirect

from test.pages.common import HomePage, LogOut
from test.utils.helpers import client_login, client_logout, response_user_logged_in, create_member

from typing import *

# test user login credentials
TEST_USER_LOGIN_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password= "testpassword",
)


class TestLogout(TestCase):
    def setUp(self) -> None:
        # set up member
        create_member(**TEST_USER_LOGIN_CREDENTIALS)
        
        self.client = Client()
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_logout_redirects_anonymous_user_to_home_page(self):
        response = self.client.get(LogOut.url)
        self.assertRedirects(response, HomePage.url, status_code=302, target_status_code=200, fetch_redirect_response=True)
    
    def test_logout_with_logged_in_user(self):
        response = client_login(self.client, TEST_USER_LOGIN_CREDENTIALS)
        self.assertTrue(response_user_logged_in(response))
        
        response = client_logout(self.client, follow=True)
        self.assertFalse(response_user_logged_in(response))

    def test_logout_redirects_to_homepage(self):
        response = client_login(self.client, TEST_USER_LOGIN_CREDENTIALS)
        self.assertTrue(response_user_logged_in(response))
        
        response = client_logout(self.client, follow=False)
        self.assertRedirects(response, HomePage.url, status_code=302, target_status_code=200, fetch_redirect_response=True)
