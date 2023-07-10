from typing import *

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.test.client import Client

from accounts.models import Member
from test.pages.common import HomePage, LogIn, SignUp
from test.utils.helpers import (client_login, client_logout, member_signup,
                                    is_redirection_target, page_in_response,
                                    response_user_logged_in, create_member)

# Create your tests here.


# new user signup data
NEW_USER_SIGNUP_DATA: Final[Dict[str, str]] = dict(
    first_name="Test",
    last_name="User",
    email="test_user@test.com",
    username="testuser2",
    password1="testpassword2",
    password2="testpassword2",
)

# new user login credentials
NEW_USER_LOGIN_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser2",
    password="testpassword2",
)

# test user login credentials
TEST_USER_LOGIN_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password="testpassword",
)


class TestSignUp(TestCase):
    
    def setUp(self) -> None:
        # set up member
        create_member(**TEST_USER_LOGIN_CREDENTIALS)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_signup_rendering(self):
        """Test that the sign up page renders correctly"""
        response = self.client.get(SignUp.get_url())
        
        self.assertEqual(response.resolver_match.view_name, SignUp.view_name)
        self.assertTemplateUsed(response, SignUp.template_name)

    def test_signup_anonymous_user_allowed(self):
        """Test that an anonymous user can access the sign up page"""
        response = self.client.get(SignUp.get_url())
        is_current_page = page_in_response(SignUp, response)
        self.assertTrue(is_current_page[0])
    
    def test_signup_logged_in_user_redirects_to_homepage(self):
        """Test that a logged in user is redirected to the home page when trying to access the sign up page"""
        response = client_login(self.client, credentials=TEST_USER_LOGIN_CREDENTIALS)
        self.assertTrue(response_user_logged_in(response))

        response = self.client.get(SignUp.get_url(), follow=True)
        
        self.assertRedirects(response, HomePage.get_url(), status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTrue(is_redirection_target(HomePage, response))
    
    def test_signup_username_required(self):
        """Test that username field is required"""
        signup_data = NEW_USER_SIGNUP_DATA.copy()
        signup_data.update({"username": ""})
        
        response = self.client.post(
            SignUp.get_url(), 
            data=signup_data, 
            follow=True
        )
        
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, SignUp.template_name)
        self.assertFormError(response.context["form"], "username", ["This field is required."])
        self.assertContains(response, "This field is required.")
    
    def test_signup_password_required(self):
        """Test that password field is required"""
        signup_data = NEW_USER_SIGNUP_DATA.copy()
        signup_data.update({"password1": "", "password2": ""})
        
        response = self.client.post(
            SignUp.get_url(), 
            data=signup_data, 
            follow=True
        )
        
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, SignUp.template_name)
        self.assertFormError(response.context["form"], "password1", ["This field is required."])
        self.assertFormError(response.context["form"], "password2", ["This field is required."])
        self.assertContains(response, "This field is required.")
        
        
    def test_signup(self):
        """Test that a new user can sign up, and is added to member database"""
        members_before_signup = Member.objects.count()
        response = member_signup(self.client, user_data=NEW_USER_SIGNUP_DATA, follow=True)
        last_member = Member.objects.last()
        
        self.assertEqual(200, response.status_code)
        self.assertRedirects(response, LogIn.get_url(), status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTrue(is_redirection_target(LogIn, response))
        
        self.assertEqual(members_before_signup + 1, Member.objects.count())
        self.assertEqual(last_member.first_name, NEW_USER_SIGNUP_DATA["first_name"])
        self.assertEqual(last_member.last_name, NEW_USER_SIGNUP_DATA["last_name"])
        self.assertEqual(last_member.email, NEW_USER_SIGNUP_DATA["email"])
        self.assertEqual(last_member.username, NEW_USER_SIGNUP_DATA["username"])
        self.assertTrue(check_password(NEW_USER_SIGNUP_DATA["password1"], last_member.password))
        self.assertTrue(last_member.is_active)
        self.assertFalse(last_member.is_staff)
        self.assertFalse(last_member.is_superuser)

    def test_signup_existing_username(self):
        """Test that a user cannot sign up with an existing username"""
        member_signup(self.client, user_data=NEW_USER_SIGNUP_DATA, follow=True)
        response = member_signup(self.client, user_data=NEW_USER_SIGNUP_DATA, follow=True)
        
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, SignUp.template_name)
        self.assertFormError(response.context["form"], "username", ["A user with that username already exists."])        
        self.assertContains(response, "A user with that username already exists.")

    def test_signup_then_login(self):
        """Test that a new user can sign up, is logged in after sign up, and can log in after signing up"""
        response = self.client.get(SignUp.get_url())
        self.assertFalse(response_user_logged_in(response))
        
        member_signup(self.client, user_data=NEW_USER_SIGNUP_DATA, follow=True)
        response = client_login(self.client, NEW_USER_LOGIN_CREDENTIALS)
        
        self.assertRedirects(response, HomePage.get_url(), status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertTrue(is_redirection_target(HomePage, response))
