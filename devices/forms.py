from typing import *

from django.forms import ModelForm, ModelChoiceField

from common.forms.mixins import UniqueDeviceGroupPerMemberMixin, UniqueDevicePerMemberMixin

from .models import Device, DeviceGroup

# Create your views here.


# -----------------------------------------------------------------------
# device group forms
# -----------------------------------------------------------------------

class DeviceGroupCreateForm(UniqueDeviceGroupPerMemberMixin, ModelForm):
    """Form to create a new device group"""
    
    class Meta:
        model = DeviceGroup
        fields = [
            "name",
            "description"
        ]
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("member")
        super().__init__(*args, **kwargs)
    
    def save(self, commit: bool = True) -> Any:
        self.instance.owner = self.owner
        return super().save(commit)


class DeviceGroupEditForm(UniqueDeviceGroupPerMemberMixin, ModelForm):
    """Device group edit form"""
    class Meta:
        model = DeviceGroup
        fields = [
            "name",
            "description",
        ]
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("member")
        super().__init__(*args, **kwargs)
    
    def save(self, commit: bool = True) -> Any:
        """Save only if data was changed"""
        if self.changed_data:
            return super().save(commit)
        return super().save(False)


# -----------------------------------------------------------------------
# device views
# -----------------------------------------------------------------------


class DeviceCreateForm(UniqueDevicePerMemberMixin, ModelForm):
    """Form to create a new device"""
    
    group = ModelChoiceField(
        queryset=DeviceGroup.objects.all(),
    )
    
    class Meta:
        model = Device
        fields = [
            "name",
        ]
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner")
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = self.owner.devicegroup_set.all()
    
    def save(self, commit: bool = True) -> Any:
        device_group = self.owner.devicegroup_set.get(name=self.cleaned_data["group"])
        device_unique_id = f"{self.owner.username}-{device_group.name}-{self.instance.name}"
        self.instance.group = device_group
        self.instance.uid = Device.generate_device_uid(device_unique_id)
        return super().save(commit)


class DeviceEditForm(UniqueDevicePerMemberMixin, ModelForm):
    """Form to edit an existing device"""
    
    group = ModelChoiceField(
        queryset=DeviceGroup.objects.all(),
    )
    
    class Meta:
        model = Device
        fields = [
            "name",
            "group",
            "is_active",
        ]
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner")
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = self.owner.devicegroup_set.all()

