from typing import *

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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


class UniqueDeviceGroupPerMemberMixin:
    """Check if device group's name is unique for the current owner, requires self.owner attribute"""
    
    error_messages = {
        "unique_name": "A device group with this name already exists.",
    }
    
    def clean_name(self) -> str:
        group_name = self.cleaned_data["name"].lower()
        if "name" in self.changed_data and self._meta.model.objects.filter(name=group_name, owner=self.owner).exists():
            raise ValidationError(
                self.error_messages["unique_name"],
                code="unique_name",
            )
        
        return group_name


class UniqueDevicePerMemberMixin:
    """Check if device's name is unique for the current owner, requires self.owner attribute"""
    
    error_messages = {
        "unique_name": "A device with this name already exists.",
    }
    
    def clean_name(self) -> str:
        device_name = self.cleaned_data["name"].lower()
        if "name" in self.changed_data and self.owner.devicegroup_set.filter(device__name__iexact=device_name).exists():
            raise ValidationError(
                self.error_messages["unique_name"],
                code="unique_name",
            )
    
        return device_name

