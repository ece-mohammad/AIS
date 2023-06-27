from typing import *

from django.contrib.auth.forms import (UserCreationForm,
                                        PasswordChangeForm, PasswordResetForm,
                                        UserChangeForm,
                                        SetPasswordForm)
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelForm, PasswordInput
from django.utils.translation import gettext_lazy as _

from .models import Member

# Create your views here.

# -----------------------------------------------------------------------------
# helper classes
# -----------------------------------------------------------------------------
class NoSaveMixin:
    def save(self, commit: bool = True) -> Any:
        commit = False
        return super().save(commit)


class UniquePasswordMixin:
    unique_password_error_messages = {
        "unique_password": _("New password must be different from old password")
    }
    
    def clean_new_password2(self) -> str:
        new_password2 = self.cleaned_data.get("new_password2")
        if self.user.check_password(new_password2):
            raise ValidationError(
                self.unique_password_error_messages["unique_password"],
                code="unique_password",
            )
        return super().clean_new_password2()


class UniqueUsernameMixin:
    unique_username_error_messages = {
        "unique_username": _("A user with that username already exists."),
    }
    
    def clean_username(self):
        """Make sure the username is unique (case insensitive), only if the username field was changed"""
        username = self.cleaned_data.get("username")
        if self.changed_data and "username" in self.changed_data and self._meta.model.objects.filter(username__iexact=username).exists():
            raise ValidationError(self.unique_username_error_messages["unique_username"], code="unique_username")
        return username

# -----------------------------------------------------------------------------
# Member Sign up form
# -----------------------------------------------------------------------------
class MemberSignUpForm(UserCreationForm):
    """User signup form"""

    error_messages = {
        "unique_username": _("A user with that username already exists."),
    }
    
    class Meta(UserCreationForm.Meta):
        model = Member 
        fields = ("first_name", "last_name", "email") + UserCreationForm.Meta.fields 


class MemberEditForm(UniqueUsernameMixin, UserChangeForm):
    """Member edit form"""
    password = None     # hide password field
    
    class Meta(UserChangeForm.Meta):
        model = Member 
        fields = ("username", "first_name", "last_name", "email")


class MemberConfirmActionForm(NoSaveMixin, ModelForm):
    """Member password form to confirm an action"""
    password = CharField(
        max_length=128,
        label=_("Password"),
        required=True,
        widget=PasswordInput(attrs={"placeholder": _("Password")}),
    )
    
    error_messages = {
        "password": {
            "required": _("Please enter your password"),
            "wrong_password": _("The password is incorrect"),
        }
    }
    
    class Meta:
        model = Member
        fields = ("password",)
    
    def clean_password(self) -> str:
        """Check password is correct"""
        password = self.cleaned_data.get("password")
        if not self.instance.check_password(password):
            raise ValidationError(message=self.error_messages["password"]["wrong_password"], code="wrong_password")
        return password


# -----------------------------------------------------------------------------
# Member Password reset, change forms
# -----------------------------------------------------------------------------
class MemberPasswordResetForm(PasswordResetForm):
    """Member password reset form"""
    pass


class MemberPasswordResetConfirmForm(UniquePasswordMixin, SetPasswordForm):
    """Member password reset confirm form"""
    pass


class MemberPasswordChangeForm(UniquePasswordMixin, PasswordChangeForm):
    """Member password change form"""
    pass

