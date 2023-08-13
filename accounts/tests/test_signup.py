from test.pages.common import HomePage, LogIn, SignUp
from test.utils.helpers import (
    client_login,
    create_member,
    member_signup,
    page_in_response,
    response_user_logged_in,
)
from typing import *

from django.test import TestCase
from pytest import mark

from accounts.models import Member

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


class BaseSignUpTestCase(TestCase):
    def setUp(self) -> None:
        # set up member
        create_member(**TEST_USER_LOGIN_CREDENTIALS)
        return super().setUp()


class TestSignUpRendering(BaseSignUpTestCase):
    def setUp(self) -> None:
        self.response = self.client.get(SignUp.get_url())
        return super().setUp()

    def test_signup_rendering(self):
        """Test that the sign up page renders correctly"""
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(page_in_response(SignUp, self.response)[0])


class TestSignUpForm(BaseSignUpTestCase):
    def setUp(self) -> None:
        self.response = self.client.get(SignUp.get_url())
        self.form = self.response.context.get("form")
        self.username_filed = self.form.fields.get("username", None)
        self.first_name_field = self.form.fields.get("first_name", None)
        self.last_name_field = self.form.fields.get("last_name", None)
        self.email_field = self.form.fields.get("email", None)
        self.password_field = self.form.fields.get("password1", None)
        self.password_confirm_field = self.form.fields.get("password2", None)
        return super().setUp()

    def test_signup_form_fields(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(len(self.form.fields), 6)
        self.assertIsNotNone(self.username_filed)
        self.assertIsNotNone(self.first_name_field)
        self.assertIsNotNone(self.last_name_field)
        self.assertIsNotNone(self.email_field)
        self.assertIsNotNone(self.password_field)
        self.assertIsNotNone(self.password_confirm_field)

    def test_signup_form_fields_username(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.username_filed.label, "Username")
        self.assertEqual(self.username_filed.required, True)
        self.assertEqual(self.username_filed.initial, None)

    def test_signup_form_fields_password(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.password_field.label, "Password")
        self.assertEqual(self.password_field.required, True)
        self.assertEqual(self.password_field.initial, None)

        self.assertEqual(self.password_confirm_field.label, "Password confirmation")
        self.assertEqual(self.password_confirm_field.required, True)
        self.assertEqual(self.password_confirm_field.initial, None)

    def test_signup_form_fields_first_name(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.first_name_field.label, "First name")
        self.assertEqual(self.first_name_field.required, False)
        self.assertEqual(self.first_name_field.initial, None)

    def test_signup_form_fields_last_name(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.last_name_field.label, "Last name")
        self.assertEqual(self.last_name_field.required, False)
        self.assertEqual(self.last_name_field.initial, None)

    def test_signup_form_fields_email(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.email_field.label, "Email address")
        self.assertEqual(self.email_field.required, False)
        self.assertEqual(self.email_field.initial, None)


class TestSignUpView(BaseSignUpTestCase):
    def test_signup_anonymous_user_allowed(self):
        """Test that an anonymous user can access the sign up page"""
        response = self.client.get(SignUp.get_url(), follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(page_in_response(SignUp, response)[0])

    def test_signup_logged_in_user_redirects_to_homepage(self):
        """Test that a logged in user is redirected to the home page when trying to access the sign up page"""
        response = client_login(self.client, credentials=TEST_USER_LOGIN_CREDENTIALS)
        self.assertTrue(response_user_logged_in(response))

        response = self.client.get(SignUp.get_url(), follow=True)
        self.assertRedirects(
            response,
            HomePage.get_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_signup_username_required(self):
        """Test that username field is required"""
        signup_data = NEW_USER_SIGNUP_DATA.copy()
        signup_data.update({"username": ""})
        response = self.client.post(SignUp.get_url(), data=signup_data, follow=True)
        form = response.context.get("form")

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, SignUp.template_name)
        self.assertFormError(form, "username", ["This field is required."])
        self.assertContains(response, "This field is required.")

    def test_signup_password_required(self):
        """Test that password field is required"""
        signup_data = NEW_USER_SIGNUP_DATA.copy()
        signup_data.update({"password1": "", "password2": ""})
        response = self.client.post(SignUp.get_url(), data=signup_data, follow=True)
        form = response.context.get("form")

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, SignUp.template_name)
        self.assertFormError(form, "password1", ["This field is required."])
        self.assertFormError(form, "password2", ["This field is required."])
        self.assertContains(response, "This field is required.")

    def test_signup_creates_new_member(self):
        """Test that a new user can sign up, and is added to member database"""
        members_before_signup = Member.objects.count()
        response = member_signup(
            self.client, user_data=NEW_USER_SIGNUP_DATA, follow=True
        )
        last_member = Member.objects.last()

        self.assertEqual(200, response.status_code)
        self.assertRedirects(
            response,
            LogIn.get_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        self.assertEqual(members_before_signup + 1, Member.objects.count())
        self.assertEqual(last_member.first_name, NEW_USER_SIGNUP_DATA["first_name"])
        self.assertEqual(last_member.last_name, NEW_USER_SIGNUP_DATA["last_name"])
        self.assertEqual(last_member.email, NEW_USER_SIGNUP_DATA["email"])
        self.assertEqual(last_member.username, NEW_USER_SIGNUP_DATA["username"])
        self.assertTrue(last_member.check_password(NEW_USER_SIGNUP_DATA["password1"]))
        self.assertTrue(last_member.is_active)
        self.assertFalse(last_member.is_staff)
        self.assertFalse(last_member.is_superuser)

    def test_signup_existing_username(self):
        """Test that a user cannot sign up with an existing username"""
        member_signup(self.client, user_data=NEW_USER_SIGNUP_DATA, follow=True)
        response = member_signup(
            self.client, user_data=NEW_USER_SIGNUP_DATA, follow=True
        )
        form = response.context.get("form")

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, SignUp.template_name)
        self.assertFormError(
            form, "username", ["A user with that username already exists."]
        )
        self.assertContains(response, "A user with that username already exists.")

    def test_signup_then_login(self):
        """Test that a new user can sign up, is logged in after sign up, and can log in after signing up"""
        response = self.client.get(SignUp.get_url())
        self.assertFalse(response_user_logged_in(response))

        member_signup(self.client, user_data=NEW_USER_SIGNUP_DATA, follow=True)
        response = client_login(self.client, NEW_USER_LOGIN_CREDENTIALS)

        self.assertRedirects(
            response,
            HomePage.get_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
