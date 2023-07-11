import re
from typing import *

from pytest import mark

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from selenium.webdriver import firefox
from selenium.webdriver.common.by import By

from test.pages.common import (HomePage, LogIn, PasswordReset,
                                PasswordResetComplete, PasswordResetConfirm,
                                PasswordResetDone)
from test.utils.helpers import client_login, create_member, page_in_response

GECKO_DRIVER_PATH: Final[str] = "/snap/bin/geckodriver"
OLD_PASSWORD: Final[str] = "old_password"
NEW_PASSWORD: Final[str] = "new_password"
MEMBER_EMAIL: Final[str] = "foo@bar.com"

TEST_USER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password=OLD_PASSWORD,
    email=MEMBER_EMAIL,
)

# password reset form locators
PASSWORD_RESET_EMAIL_LOCATOR: Final[Tuple[str, str]] = (By.CSS_SELECTOR, "#id_email")
PASSWORD_RESET_SUBMIT_LOCATOR: Final[Tuple[str, str]] = (By.CSS_SELECTOR, "[type='submit']")

# password reset confirm form locators
PASSWORD_RESET_CONFIRM_NEW_PASSWORD_LOCATOR = (By.CSS_SELECTOR, "#id_new_password1")
PASSWORD_RESET_CONFIRM_NEW_PASSWORD_CONFIRM_LOCATOR = (By.CSS_SELECTOR, "#id_new_password2")
PASSWORD_RESET_CONFIRM_SUBMIT_LOCATOR = (By.CSS_SELECTOR, "[type='submit']")

# login page locators
LOGIN_USERNAME_LOCATOR: Final[Tuple[str, str]] = (By.CSS_SELECTOR, "#id_username")
LOGIN_PASSWORD_LOCATOR: Final[Tuple[str, str]] = (By.CSS_SELECTOR, "#id_password")
LOGIN_SUBMIT_LOCATOR: Final[Tuple[str, str]] = (By.CSS_SELECTOR, "[type='submit']")


class TestPasswordResetTemplates(TestCase):
    def setUp(self) -> None:
        create_member(**TEST_USER_CREDENTIALS)
        return super().setUp()
    
    def test_password_reset_template_rendering(self):
        response = self.client.get(PasswordReset.get_url())
        is_password_reset_page = page_in_response(PasswordReset, response)
        
        self.assertTemplateUsed(response, PasswordReset.template_name)
        self.assertTrue(is_password_reset_page[0])
    
    def test_password_reset_done_template_rendering(self):
        response = self.client.get(PasswordResetDone.get_url())
        is_password_reset_done_page = page_in_response(PasswordResetDone, response)
        
        self.assertTemplateUsed(response, PasswordResetDone.template_name)
        self.assertTrue(is_password_reset_done_page[0])
    
    def test_password_reset_complete_rendering(self):
        response = self.client.get(PasswordResetComplete.get_url())
        is_password_reset_complete_page = page_in_response(PasswordResetComplete, response)
        
        self.assertTemplateUsed(response, PasswordResetComplete.template_name)
        self.assertTrue(is_password_reset_complete_page[0])


class TestPasswordResetForms(TestCase):

    def test_password_reset_form_email_field_required(self):
        response = self.client.post(PasswordReset.get_url(), data=dict(email=""))
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "email", ["This field is required."])
        self.assertContains(response, "This field is required.")
    
    def test_password_reset_form_invalid_email(self):
        response = self.client.post(PasswordReset.get_url(), data=dict(email="invalid_email"))
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "email", ["Enter a valid email address."])
        self.assertContains(response, "Enter a valid email address.")
        
    def test_password_reset_form_valid_email(self):
        response = self.client.post(PasswordReset.get_url(), data=dict(email="email@mail.com"))
        self.assertRedirects(response, PasswordResetDone.get_url())


class TestPasswordResetView(TestCase):
    def setUp(self) -> None:
        create_member(**TEST_USER_CREDENTIALS)
        return super().setUp()
        
    def test_password_reset_redirects_logged_in_user(self):
        client_login(self.client, TEST_USER_CREDENTIALS)
        response = self.client.get(PasswordReset.get_url())
        self.assertRedirects(response, HomePage.get_url())


class TestPasswordResetSequence(StaticLiveServerTestCase):
    """Test password reset using selenium & firefox"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        create_member(**TEST_USER_CREDENTIALS)
        cls.selenium = cls.get_firefox_webdriver()
        cls.selenium.implicitly_wait(10)
        
    @classmethod
    def tearDownClass(cls) -> None:
        cls.selenium.quit()
        super().tearDownClass()
    
    @classmethod
    def get_firefox_webdriver(cls) -> firefox.webdriver.WebDriver:
        options = firefox.options.Options()
        options.add_argument("--headless")
        service = firefox.service.Service(executable_path=GECKO_DRIVER_PATH)
        return firefox.webdriver.WebDriver(service=service, options=options)
    
    def get_password_reset_address(self, sender: str, to: str) -> str|None:
        """Get password reset token from email."""
        for email_message in mail.outbox:
            if (email_message.from_email == sender) and (to in email_message.to):
                password_reset_url = re.search(r"http://.+/accounts/password_reset/confirm/.+/", email_message.body)
                return password_reset_url.group(0) if password_reset_url else None
    
    @mark.slow
    def test_password_reset_sequence(self):
        # open password reset page
        self.selenium.get(f"{self.live_server_url}/{PasswordReset.get_url()}")
        self.assertEqual(self.selenium.title, PasswordReset.title)
        
        # enter email address
        self.selenium.find_element(*PASSWORD_RESET_EMAIL_LOCATOR).send_keys(MEMBER_EMAIL)
        self.selenium.find_element(*PASSWORD_RESET_SUBMIT_LOCATOR).click()
        self.assertEqual(self.selenium.title, PasswordResetDone.title)
        
        # get password reset email
        password_reset_url = self.get_password_reset_address(sender="webmaster@localhost", to=MEMBER_EMAIL)
        self.assertIsNotNone(password_reset_url)
        
        # open password reset url
        self.selenium.get(f"{password_reset_url}")
        self.assertEqual(self.selenium.title, PasswordResetConfirm.title)
        
        # enter new password
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_NEW_PASSWORD_LOCATOR).send_keys(NEW_PASSWORD)
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_NEW_PASSWORD_CONFIRM_LOCATOR).send_keys(NEW_PASSWORD)
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_SUBMIT_LOCATOR).click()
        self.assertEqual(self.selenium.title, PasswordResetComplete.title)
        
        # login using new password
        self.selenium.get(f"{self.live_server_url}/{LogIn.get_url()}")
        self.selenium.find_element(*LOGIN_USERNAME_LOCATOR).send_keys(TEST_USER_CREDENTIALS["username"])
        self.selenium.find_element(*LOGIN_PASSWORD_LOCATOR).send_keys(NEW_PASSWORD)
        self.selenium.find_element(*LOGIN_SUBMIT_LOCATOR).click()
        self.assertEqual(self.selenium.title, HomePage.title)
        
    @mark.slow
    def test_password_reset_unique_password(self):
        # open password reset page
        self.selenium.get(f"{self.live_server_url}/{PasswordReset.get_url()}")
        self.assertEqual(self.selenium.title, PasswordReset.title)
        
        # enter email address
        self.selenium.find_element(*PASSWORD_RESET_EMAIL_LOCATOR).send_keys(MEMBER_EMAIL)
        self.selenium.find_element(*PASSWORD_RESET_SUBMIT_LOCATOR).click()
        self.assertEqual(self.selenium.title, PasswordResetDone.title)
        
        # get password reset email
        password_reset_url = self.get_password_reset_address(sender="webmaster@localhost", to=MEMBER_EMAIL)
        self.assertIsNotNone(password_reset_url)
        
        # open password reset url
        self.selenium.get(f"{password_reset_url}")
        self.assertEqual(self.selenium.title, PasswordResetConfirm.title)
        
        # enter old password
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_NEW_PASSWORD_LOCATOR).send_keys(OLD_PASSWORD)
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_NEW_PASSWORD_CONFIRM_LOCATOR).send_keys(OLD_PASSWORD)
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_SUBMIT_LOCATOR).click()
        self.assertEqual(self.selenium.title, PasswordResetConfirm.title)
        self.assertInHTML("New password must be different from old password", self.selenium.page_source)


