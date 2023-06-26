import re
import time
from typing import *

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
        self.client = Client()
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
    def setUp(self) -> None:
        self.client = Client()
        return super().setUp()

    def test_password_reset_form_email_field(self):
        response = self.client.post(PasswordReset.get_url(), data=dict(email=""))
        self.assertFormError(response, "form", "email", "This field is required.")
    
    def test_password_reset_form_invalid_email(self):
        response = self.client.post(PasswordReset.get_url(), data=dict(email="invalidemail"))
        self.assertFormError(response, "form", "email", "Enter a valid email address.")
        
    def test_password_reset_form_valid_email(self):
        response = self.client.post(PasswordReset.get_url(), data=dict(email="email@mail.com"))
        self.assertRedirects(response, PasswordResetDone.get_url())


class TestPasswordResetView(TestCase):
    def setUp(self) -> None:
        create_member(**TEST_USER_CREDENTIALS)
        self.client = Client()
        return super().setUp()        
        
    def test_password_reset_redirects_logged_in_user(self):
        client_login(self.client, TEST_USER_CREDENTIALS)
        response = self.client.get(PasswordReset.get_url())
        self.assertRedirects(response, HomePage.get_url())


class TestPasswordResetSequence(StaticLiveServerTestCase):
    
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
        service = firefox.service.Service(executable_path=GECKO_DRIVER_PATH)
        return firefox.webdriver.WebDriver(service=service)
    
    def get_password_reset_address(self, sender: str, to: str) -> str|None:
        """Get password reset token from email."""
        for email_message in mail.outbox:
            if (email_message.from_email == sender) and (to in email_message.to):
                password_reset_url = re.search(r"http://.+/accounts/password_reset/confirm/.+/", email_message.body)
                return password_reset_url.group(0) if password_reset_url else None
    
    def test_password_reset_sequence(self):
        self.selenium.get(f"{self.live_server_url}/{PasswordReset.get_url()}")
        self.assertEqual(self.selenium.title, PasswordReset.title)
        
        self.selenium.find_element(*PASSWORD_RESET_EMAIL_LOCATOR).send_keys(MEMBER_EMAIL)
        self.selenium.find_element(*PASSWORD_RESET_SUBMIT_LOCATOR).click()
        self.assertEqual(self.selenium.title, PasswordResetDone.title)
        
        password_reset_url = self.get_password_reset_address(sender="webmaster@localhost", to=MEMBER_EMAIL)
        self.assertIsNotNone(password_reset_url)
        self.selenium.get(f"{password_reset_url}")
        self.assertEqual(self.selenium.title, PasswordResetConfirm.title)
        
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_NEW_PASSWORD_LOCATOR).send_keys(NEW_PASSWORD)
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_NEW_PASSWORD_CONFIRM_LOCATOR).send_keys(NEW_PASSWORD)
        self.selenium.find_element(*PASSWORD_RESET_CONFIRM_SUBMIT_LOCATOR).click()
        self.assertEqual(self.selenium.title, PasswordResetComplete.title)
        time.sleep(5)
        
        self.selenium.get(f"{self.live_server_url}/{LogIn.get_url()}")
        self.selenium.find_element(*LOGIN_USERNAME_LOCATOR).send_keys(TEST_USER_CREDENTIALS["username"])
        self.selenium.find_element(*LOGIN_PASSWORD_LOCATOR).send_keys(NEW_PASSWORD)
        self.selenium.find_element(*LOGIN_SUBMIT_LOCATOR).click()
        self.assertEqual(self.selenium.title, HomePage.title)
        time.sleep(1)
        
        # self.client.get(PasswordReset.url)
        # self.client.post(PasswordReset.url, data=dict(email=MEMBER_EMAIL))
        
        # self.assertEqual(1, len(mail.outbox))
        # self.assertEqual(mail.outbox[0].subject, "Password reset on testserver")
        
        # password_reset_address = self.get_password_reset_address(sender="webmaster@localhost", to=MEMBER_EMAIL)
        # response = self.client.get(password_reset_address, follow=False)
        
        # new_password_url = response.url
        
        # response = self.client.get(new_password_url)
        # response = self.client.post(
        #     new_password_url,
        #     data = dict(
        #         new_password1=NEW_PASSWORD,
        #         new_password2=NEW_PASSWORD,
        #     )
        # )
        # print(*[t.name for t in response.templates], sep="\n")

