from typing import *

from django.db.models import Count, F, QuerySet
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from common.views.mixins import (DeviceGroupOwnerMixin, DeviceOwnerMixin,
                                    MemberLoginRequiredMixin)

from accounts.forms import MemberConfirmActionForm

from .forms import (DeviceCreateForm, DeviceEditForm, DeviceGroupCreateForm,
                    DeviceGroupEditForm)
from .models import Device, DeviceGroup

# Create your views here.

# -----------------------------------------------------------------------
# device group views
# -----------------------------------------------------------------------
class BaseDeviceGroupView(MemberLoginRequiredMixin, DeviceGroupOwnerMixin):
    model = DeviceGroup


class BaseDeviceGroupEditView(BaseDeviceGroupView):
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add owner to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs


class DeviceGroupCreateView(BaseDeviceGroupEditView, CreateView):
    """Create a new device group"""
    # model = DeviceGroup
    form_class = DeviceGroupCreateForm
    template_name = "devices/group/create.html"

    # def get_form_kwargs(self) -> Dict[str, Any]:
    #     """Add owner to form kwargs"""
    #     kwargs = super().get_form_kwargs()
    #     kwargs["owner"] = self.request.user
    #     return kwargs

class DeviceGroupDetailView(BaseDeviceGroupView, DetailView):
    """Details view for a device group"""
    # model = DeviceGroup
    template_name = "devices/group/details.html"
    context_object_name = "device_group"
    slug_field = "name"
    slug_url_kwarg = "group_name"


class DeviceGroupListView(MemberLoginRequiredMixin, DeviceGroupOwnerMixin, ListView):
    """List all device groups for the current user"""
    model = DeviceGroup
    context_object_name = "device_groups"
    template_name = "devices/group/list.html"
    allow_empty = True
    
    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        return qs.annotate(device_count=Count("device"))


class DeviceGroupEditView(MemberLoginRequiredMixin, DeviceGroupOwnerMixin, UpdateView):
    """Device group edit view"""
    model = DeviceGroup
    form_class = DeviceGroupEditForm
    template_name = "devices/group/edit.html"
    context_object_name = "device_group"
    slug_field = "name"
    slug_url_kwarg = "group_name"
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add owner to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs


class DeviceGroupDeleteView(MemberLoginRequiredMixin, DeviceGroupOwnerMixin, DeleteView):
    """Delete device group"""
    model = DeviceGroup
    # form_class = MemberConfirmActionForm
    template_name = "devices/group/delete.html"
    success_url = reverse_lazy("devices:group_list")
    context_object_name = "device_group"
    slug_field = "name"
    slug_url_kwarg = "group_name"


# -----------------------------------------------------------------------
# device views
# -----------------------------------------------------------------------
class DeviceCreateView(MemberLoginRequiredMixin, CreateView):
    model = Device
    form_class = DeviceCreateForm
    template_name = "devices/device/create.html"
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs


class DeviceListView(MemberLoginRequiredMixin, DeviceOwnerMixin, ListView):
    model = Device
    fields = [
        'name', 
        "uid",
        'group',
        'owner',
        'date_added',
        'last_updated',
        'is_active'
    ]

    template_name = 'devices/device/list.html'
    context_object_name = 'device_list'
    
    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset().filter(is_active=True).annotate(
            group_name=F("group__name"),
            owner_name=F("group__owner__username"),
        ).order_by("group_name", "name")
        return qs


class DeviceDetailView(MemberLoginRequiredMixin, DeviceOwnerMixin, DetailView):
    model = Device
    fields = [
        "name",
        "uid",
        "date_added",
        "group",
        "is_active",
    ]

    template_name = "devices/device/details.html"
    context_object_name = "device"
    slug_field = "uid"
    slug_url_kwarg = "device_uid"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data =  super().get_context_data(**kwargs)
        context_data["device_group"] = self.object.group
        context_data["device_owner"] = self.object.group.owner
        return context_data


class DeviceEditView(MemberLoginRequiredMixin, DeviceOwnerMixin, UpdateView):
    model = Device
    form_class = DeviceEditForm
    template_name = "devices/device/edit.html"
    slug_field = "uid"
    slug_url_kwarg = "device_uid"

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs


class DeviceDeleteView(MemberLoginRequiredMixin, DeviceOwnerMixin, DeleteView):
    model = Device
    # form_class = MemberConfirmActionForm
    template_name = "devices/device/delete.html"
    success_url = reverse_lazy("devices:device_list")
    slug_field = "uid"
    slug_url_kwarg = "device_uid"

