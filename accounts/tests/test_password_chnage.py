from test.pages.common import HomePage, PasswordChange, PasswordChangeDone
from test.utils.helpers import (
    client_login,
    client_logout,
    create_member,
    page_title_in_response,
)
from typing import *

from django.test import TestCase
from django.test.client import Client

OLD_PASSWORD: Final[str] = "old_password"
NEW_PASSWORD: Final[str] = "new_password"

MEMBER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password=OLD_PASSWORD,
)


class BasePasswordChangeTestCase(TestCase):
    def setUp(self) -> None:
        create_member(**MEMBER_CREDENTIALS)

        self.client: Client = Client()
        client_login(self.client, MEMBER_CREDENTIALS)

        return super().setUp()


class TestPasswordChangeRendering(BasePasswordChangeTestCase):
    def test_password_change_rendering(self):
        response = self.client.get(PasswordChange.get_url())
        self.assertTemplateUsed(response, PasswordChange.template_name)
        self.assertTrue(page_title_in_response(PasswordChange, response))


class TestPasswordChangeForm(BasePasswordChangeTestCase):
    def setUp(self):
        ret = super().setUp()
        self.response = self.client.get(PasswordChange.get_url())
        self.form = self.response.context.get("form")
        self.old_password_field = self.form.fields.get("old_password")
        self.new_password_field = self.form.fields.get("new_password1")
        self.new_password_confirm_field = self.form.fields.get("new_password2")
        return ret

    def test_password_change_form_fields(self):
        self.assertIsNotNone(self.form)
        self.assertIsNotNone(self.old_password_field)
        self.assertIsNotNone(self.new_password_field)
        self.assertIsNotNone(self.new_password_confirm_field)

    def test_password_change_form_field_old_password(self):
        self.assertEqual(self.old_password_field.label, "Old password")
        self.assertEqual(self.old_password_field.required, True)
        self.assertEqual(self.old_password_field.initial, None)

    def test_password_change_form_field_new_password(self):
        self.assertEqual(self.new_password_field.label, "New password")
        self.assertEqual(self.new_password_field.required, True)
        self.assertEqual(self.new_password_field.initial, None)

    def test_password_change_form_field_new_password_confirm(self):
        self.assertEqual(
            self.new_password_confirm_field.label, "New password confirmation"
        )
        self.assertEqual(self.new_password_confirm_field.required, True)
        self.assertEqual(self.new_password_confirm_field.initial, None)


class TestPasswordChange(BasePasswordChangeTestCase):
    def test_password_change_form_old_password_required(self):
        response = self.client.post(
            PasswordChange.get_url(),
            dict(
                new_password1=NEW_PASSWORD,
                new_password2=NEW_PASSWORD,
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context.get("form"), "old_password", ["This field is required."]
        )
        self.assertContains(response, "This field is required.")

    def test_password_change_form_wrong_old_password(self):
        response = self.client.post(
            PasswordChange.get_url(),
            dict(
                old_password="wrong_password",
                new_password1=NEW_PASSWORD,
                new_password2=NEW_PASSWORD,
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context.get("form"),
            "old_password",
            ["Your old password was entered incorrectly. Please enter it again."],
        )
        self.assertContains(
            response,
            "Your old password was entered incorrectly. Please enter it again.",
        )

    def test_password_change_form_new_password_mismatch(self):
        response = self.client.post(
            PasswordChange.get_url(),
            dict(
                old_password=OLD_PASSWORD,
                new_password1="wrong_password",
                new_password2=NEW_PASSWORD,
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context.get("form"),
            "new_password2",
            ["The two password fields didn’t match."],
        )
        self.assertContains(response, "The two password fields didn’t match.")

    def test_password_change_redirects_anonymous_user(self):
        client = Client()
        response = client.get(PasswordChange.get_url(), follow=False)
        self.assertEqual(response.status_code, 302)

    def test_password_change_sequence(self):
        response = self.client.post(
            PasswordChange.get_url(),
            {
                "old_password": OLD_PASSWORD,
                "new_password1": NEW_PASSWORD,
                "new_password2": NEW_PASSWORD,
            },
        )
        self.assertRedirects(response, PasswordChangeDone.get_url())

        response = client_logout(self.client)
        self.assertIsNone(self.client.session.session_key)

        response = client_login(
            self.client,
            dict(
                username=MEMBER_CREDENTIALS["username"],
                password=NEW_PASSWORD,
                follow=False,
            ),
        )
        self.assertRedirects(response, HomePage.get_url())
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertIsNotNone(self.client.session.session_key)
