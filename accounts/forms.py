from typing import *

from django.contrib.auth.forms import (BaseUserCreationForm,
                                        PasswordChangeForm, PasswordResetForm,
                                        UserChangeForm)
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

# -----------------------------------------------------------------------------
# Member Sign up form
# -----------------------------------------------------------------------------
class MemberSignUpForm(BaseUserCreationForm):
    """User signup form"""
    class Meta(BaseUserCreationForm.Meta):
        model = Member 
        fields = ("first_name", "last_name", "email") + BaseUserCreationForm.Meta.fields 


class MemberEditForm(UserChangeForm):
    """Member edit form"""
    class Meta(UserChangeForm.Meta):
        model = Member 
        # fields = ("first_name", "last_name", "email")


class MemberDeactivateForm(NoSaveMixin, ModelForm):
    """Member deactivate form"""
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


class MemberPasswordResetConfirmForm(PasswordResetForm):
    """Member password reset confirm form"""
    pass


class MemberPasswordChangeForm(PasswordChangeForm):
    """Member password change form"""
    
    error_messages = {
        **PasswordChangeForm.error_messages,
        "invalid_new_password": _("New password must be different from old password"),
    }
    
    # check new password is different from old password
    def clean_new_password2(self) -> str:
        new_password1 = self.cleaned_data.get("new_password1")
        old_password = self.cleaned_data.get("old_password")
        
        # add error to new_password1 field
        if self.user.check_password(new_password1) or new_password1 == old_password:
            raise ValidationError(
                self.error_messages["invalid_new_password"],
                code="invalid_new_password",
            )
        
        return super().clean_new_password2()

