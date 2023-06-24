from typing import *

from django.core.exceptions import ValidationError
from django.contrib.auth.forms import BaseUserCreationForm, PasswordChangeForm, PasswordResetForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from .models import Member

# Create your views here.

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

