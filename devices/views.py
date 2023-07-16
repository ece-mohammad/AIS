from typing import *

from django.db.models import Count, F, QuerySet
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from accounts.forms import MemberConfirmActionForm
from common.views.mixins import (DeviceGroupOwnerMixin, DevicesByMemberMixin,
                                    DeviceBySlugMixin,
                                    MemberLoginRequiredMixin)

from .forms import (DeviceCreateForm, DeviceEditForm, DeviceGroupCreateForm,
                    DeviceGroupEditForm)
from .models import Device, DeviceGroup

# Create your views here.

# -----------------------------------------------------------------------
# Base device group views
# -----------------------------------------------------------------------
class BaseDeviceGroupView(MemberLoginRequiredMixin, DeviceGroupOwnerMixin):
    model = DeviceGroup

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add owner to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs["member"] = self.request.user
        return kwargs


class BaseDeviceGroupEditView(BaseDeviceGroupView):
    slug_field = "name"
    slug_url_kwarg = "group_name"


# -----------------------------------------------------------------------
# device group views
# -----------------------------------------------------------------------
class DeviceGroupCreateView(BaseDeviceGroupView, CreateView):
    """Create a new device group"""
    form_class = DeviceGroupCreateForm
    template_name = "devices/group/create.html"


class DeviceGroupListView(BaseDeviceGroupView, ListView):
    """List all device groups for the current user"""
    context_object_name = "device_groups"
    template_name = "devices/group/list.html"
    allow_empty = True
    
    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        return qs.annotate(device_count=Count("device"))


class DeviceGroupDetailView(BaseDeviceGroupEditView, DetailView):
    """Details view for a device group"""
    template_name = "devices/group/details.html"
    context_object_name = "device_group"


class DeviceGroupEditView(BaseDeviceGroupEditView, UpdateView):
    """Device group edit view"""
    form_class = DeviceGroupEditForm
    template_name = "devices/group/edit.html"
    context_object_name = "device_group"


class DeviceGroupDeleteView(BaseDeviceGroupEditView, DeleteView):
    """Delete device group"""
    form_class = MemberConfirmActionForm
    template_name = "devices/group/delete.html"
    success_url = reverse_lazy("devices:group_list")
    context_object_name = "device_group"


# -----------------------------------------------------------------------
# Base Device views
# -----------------------------------------------------------------------
class BaseDeviceView(MemberLoginRequiredMixin):
    model = Device 


class BaseDeviceWithMemberFormView(BaseDeviceView):
    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["member"] = self.request.user
        return kwargs


class BaseDeviceBtSlugDetailsView(BaseDeviceView, DeviceBySlugMixin):
    ...


class BaseDeviceBySlugEditView(BaseDeviceWithMemberFormView, DeviceBySlugMixin):
    ...

# -----------------------------------------------------------------------
# Device views
# -----------------------------------------------------------------------
class DeviceCreateView(BaseDeviceWithMemberFormView, CreateView):
    form_class = DeviceCreateForm
    template_name = "devices/device/create.html"


class DeviceListView(BaseDeviceView, DevicesByMemberMixin, ListView):
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


class DeviceDetailView(BaseDeviceBtSlugDetailsView, DetailView):
    fields = [
        "name",
        "uid",
        "date_added",
        "group",
        "is_active",
    ]

    template_name = "devices/device/details.html"
    context_object_name = "device"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data =  super().get_context_data(**kwargs)
        context_data["device_group"] = self.object.group
        context_data["device_owner"] = self.object.group.owner
        return context_data


class DeviceEditView(BaseDeviceBySlugEditView, UpdateView):
    form_class = DeviceEditForm
    template_name = "devices/device/edit.html"


class DeviceDeleteView(BaseDeviceBySlugEditView, DeleteView):
    form_class = MemberConfirmActionForm
    template_name = "devices/device/delete.html"
    success_url = reverse_lazy("devices:device_list")
