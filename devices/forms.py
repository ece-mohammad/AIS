from distutils.command import clean
from typing import *

from django.db.models import TextChoices
from django.forms import ModelChoiceField, ModelForm, Form, CharField, ChoiceField
from django.utils.translation import gettext_lazy as _

from common.forms.mixins import (UniqueDeviceGroupPerMemberMixin,
                                    UniqueDevicePerMemberMixin)

from .models import Device, DeviceGroup

# Create your views here.


# -----------------------------------------------------------------------
# device group forms
# -----------------------------------------------------------------------
class BaseDeviceGroupForm(UniqueDeviceGroupPerMemberMixin, ModelForm):
    class Meta:
        model = DeviceGroup
        fields = [
            "name",
            "description"
        ]
        
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("member")
        super().__init__(*args, **kwargs)


class DeviceGroupCreateForm(BaseDeviceGroupForm):
    """Form to create a new device group"""
    def save(self, commit: bool = True) -> Any:
        self.instance.owner = self.owner
        return super().save(commit)


class DeviceGroupEditForm(BaseDeviceGroupForm):
    """Device group edit form"""
    def save(self, commit: bool = True) -> Any:
        """Save only if data was changed"""
        if self.changed_data:
            return super().save(commit)
        return super().save(False)


# -----------------------------------------------------------------------
# device forms
# -----------------------------------------------------------------------
class BaseDeviceForm(UniqueDevicePerMemberMixin, ModelForm):
    group = ModelChoiceField(
        queryset=DeviceGroup.objects.all(),
    )
    
    class Meta:
        model = Device
        fields = [
            "name",
        ]
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("member")
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = self.owner.devicegroup_set.all()


class DeviceCreateForm(BaseDeviceForm):
    """Form to create a new device"""
    def save(self, commit: bool = True) -> Any:
        device_group = self.owner.devicegroup_set.get(name=self.cleaned_data["group"])
        device_unique_id = f"{self.owner.username}-{device_group.name}-{self.instance.name}"
        self.instance.group = device_group
        self.instance.uid = Device.generate_device_uid(device_unique_id)
        return super().save(commit)


class DeviceEditForm(BaseDeviceForm):
    """Form to edit an existing device"""
    
    class Meta(BaseDeviceForm.Meta):
        fields = BaseDeviceForm.Meta.fields + [
            "group",
            "is_active",
        ]


# -----------------------------------------------------------------------
# Search form
# -----------------------------------------------------------------------
class DeviceSearchForm(Form):
    class SearchFor(TextChoices):
        DEVICE = "device", _("Device")
        GROUP = "group", _("Group")
        
    """Form to search for devices, or device groups"""
    name = CharField(
        max_length=100, 
        label=_("Name"),
        required=False,
    )
    
    search_for = ChoiceField(
        choices=SearchFor.choices, 
        label=_("Search For"), 
        required=False, 
        initial=SearchFor.DEVICE,
    )
    
    def clean_name(self) -> str:
        """Validate name"""
        name = self.cleaned_data["name"]
        if name:
            return name.strip()
        return name.lower()
