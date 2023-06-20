from typing import *

from django.contrib.auth.forms import BaseUserCreationForm, PasswordChangeForm, PasswordResetForm, UserChangeForm

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
        # fields = ("first_name", "last_name", "email") + UserChangeForm.Meta.fields


# -----------------------------------------------------------------------------
# Member Password reset, change forms
# -----------------------------------------------------------------------------
class MemberPasswordResetForm(PasswordResetForm):
    """Member password reset form"""
    pass 


class MemberPasswordChangeForm(PasswordChangeForm):
    """Member password change form"""
    pass



