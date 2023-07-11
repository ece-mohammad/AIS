from typing import *

from django.contrib.auth.forms import (PasswordChangeForm, PasswordResetForm,
                                        SetPasswordForm, UserChangeForm,
                                        UserCreationForm)
from django.core.exceptions import ValidationError
from django.forms import CharField, Form, PasswordInput
from django.utils.translation import gettext_lazy as _

from common.forms.mixins import UniquePasswordMixin, UniqueUsernameMixin

from .models import Member

# Create your views here.



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


class MemberConfirmActionForm(Form):
    """
    A form to confirm an member's password. Used to prompt user to enter their password to confirm an action.
    Requires Member instance as `member` kwarg to be passed to the form's constructor.
    """
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
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        self.member = kwargs.pop("member")
        super().__init__(*args, **kwargs)
    
    def clean_password(self) -> str:
        """Check password is correct"""
        """
        password = self.cleaned_data.get("password")
        if not "password" in self.changed_data and not self.member.check_password(password):
            raise ValidationError(message=self.error_messages["password"]["wrong_password"], code="wrong_password")
        return password
        """
        password = self.cleaned_data.get("password")
        if not self.member.check_password(password):
            raise ValidationError(message=self.error_messages["password"]["wrong_password"], code="wrong_password")
        return password
    
    def save(self, commit: bool = True) -> Any:
        """Do nothing, as this form is only used to confirm password"""
        if self.instance:
            self.instance
        else:
            return self.member


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

