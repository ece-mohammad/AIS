from typing import *

from django.conf import settings
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Count, F, Q, QuerySet
from django.db.models.query import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView

from accounts.forms import MemberConfirmActionForm
from common.views.mixins import MemberLoginRequiredMixin

from .forms import (
    DeviceCreateForm,
    DeviceEditForm,
    DeviceGroupCreateForm,
    DeviceGroupEditForm,
    DeviceSearchForm,
)
from .models import Device, DeviceData, DeviceGroup

# Create your views here.


class SearchBarMixin:
    extra_context = dict(
        search_form=DeviceSearchForm(),
    )


# -----------------------------------------------------------------------
# Device Group Mixins
# -----------------------------------------------------------------------
class DeviceGroupByOwnerMixin:
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(owner=self.request.user)


# -----------------------------------------------------------------------
# Device Mixins
# -----------------------------------------------------------------------
class DevicesByOwnerMixin:
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(group__owner=self.request.user)


class DeviceBySlugMixin(DevicesByOwnerMixin):
    slug_field = "uid"
    slug_url_kwarg = "device_uid"


# -----------------------------------------------------------------------
# Base device group views
# -----------------------------------------------------------------------
class BaseDeviceGroupView(
    MemberLoginRequiredMixin, SearchBarMixin, DeviceGroupByOwnerMixin
):
    model = DeviceGroup

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add owner to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs["member"] = self.request.user
        return kwargs


class BaseDeviceGroupBySlugView(BaseDeviceGroupView):
    slug_field = "name"
    slug_url_kwarg = "group_name"


class BaseDeviceGroupEditView(BaseDeviceGroupBySlugView):
    extra_context = None


# -----------------------------------------------------------------------
# device group views
# -----------------------------------------------------------------------
class DeviceGroupCreateView(BaseDeviceGroupView, CreateView):
    """Create a new device group"""

    form_class = DeviceGroupCreateForm
    template_name = "devices/group/create.html"
    extra_context = None


class DeviceGroupListView(BaseDeviceGroupView, ListView):
    """List all device groups for the current user"""

    context_object_name = "device_groups"
    template_name = "devices/group/list.html"
    allow_empty = True
    paginate_by = settings.PAGINATION_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        return qs.annotate(device_count=Count("device"))


class DeviceGroupDetailView(BaseDeviceGroupBySlugView, DetailView):
    """Details view for a device group"""

    template_name = "devices/group/details.html"
    context_object_name = "device_group"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["device_count"] = self.object.device_set.count()
        context["device_list"] = self.object.device_set.all()
        return context


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
class BaseDeviceView(MemberLoginRequiredMixin, SearchBarMixin):
    model = Device


class BaseDeviceWithMemberFormView(BaseDeviceView):
    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["member"] = self.request.user
        return kwargs


class BaseDeviceBySlugDetailsView(BaseDeviceView, DeviceBySlugMixin):
    ...


class BaseDeviceBySlugEditView(BaseDeviceWithMemberFormView, DeviceBySlugMixin):
    extra_context = None


# -----------------------------------------------------------------------
# Device views
# -----------------------------------------------------------------------
class DeviceCreateView(BaseDeviceWithMemberFormView, CreateView):
    form_class = DeviceCreateForm
    template_name = "devices/device/create.html"


class DeviceListView(BaseDeviceView, DevicesByOwnerMixin, ListView):
    fields = [
        "name",
        "uid",
        "group",
        "owner",
        "date_added",
        "last_updated",
        "is_active",
    ]
    template_name = "devices/device/list.html"
    context_object_name = "device_list"
    paginate_by = settings.PAGINATION_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        qs = (
            super()
            .get_queryset()
            .filter(is_active=True)
            .annotate(
                group_name=F("group__name"),
                owner_name=F("group__owner__username"),
            )
            .order_by("group_name", "name")
        )
        return qs


class DeviceDetailView(BaseDeviceBySlugDetailsView, DetailView):
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
        context_data = super().get_context_data(**kwargs)
        context_data["device_group"] = self.object.group
        context_data["device_owner"] = self.object.group.owner
        context_data["device_data_list"] = self.object.devicedata_set.all().order_by(
            "-date"
        )[: settings.MOST_RECENT_SIZE]
        last_data = context_data["device_data_list"].first()
        context_data["last_update"] = last_data.date if last_data else None
        return context_data


class DeviceEditView(BaseDeviceBySlugEditView, UpdateView):
    form_class = DeviceEditForm
    template_name = "devices/device/edit.html"


class DeviceDeleteView(BaseDeviceBySlugEditView, DeleteView):
    form_class = MemberConfirmActionForm
    template_name = "devices/device/delete.html"
    success_url = reverse_lazy("devices:device_list")


class DeviceDataHistoryView(BaseDeviceBySlugDetailsView, ListView):
    template_name = "devices/device/data_history.html"
    context_object_name = "device_data_list"
    paginate_by = settings.PAGINATION_SIZE

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.device = get_object_or_404(
            Device, uid=kwargs["device_uid"], group__owner=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["device"] = self.device
        return context

    def get_queryset(self) -> QuerySet[Any]:
        return self.device.devicedata_set.all().order_by("-date")


# -----------------------------------------------------------------------
# Device Data views
# -----------------------------------------------------------------------
class BaseDeviceDataView(MemberLoginRequiredMixin, SearchBarMixin):
    model = DeviceData


class DeviceDataByMember(BaseDeviceDataView):
    def get_queryset(self) -> QuerySet[Any]:
        # TODO active devices only
        device_member_filter = Q(
            device__group__owner=self.request.user
        )  # & Q(device__is_active=True)
        return super().get_queryset().filter(device_member_filter)


class DeviceDataDetailsView(DeviceDataByMember, DetailView):
    template_name = "devices/data/details.html"
    context_object_name = "device_data"


class DeviceDataListView(DeviceDataByMember, ListView):
    template_name = "devices/data/list.html"
    context_object_name = "device_data_list"
    ordering = ["-date"]
    paginate_by = settings.PAGINATION_SIZE


# -----------------------------------------------------------------------
# DeviceGroup/Device Search View
# -----------------------------------------------------------------------
class DeviceSearchResultsView(MemberLoginRequiredMixin, FormView):
    form_class = DeviceSearchForm
    paginate_by = settings.PAGINATION_SIZE
    allow_empty = True
    queryset = None
    model = Device
    paginate_orphans = 0
    paginator_class = Paginator
    page_kwarg = "page"
    context_object_name = "search_results"
    ordering = ["name"]
    template_name = "devices/search.html"

    def get_queryset(self):
        search_for = self.request.GET.get("search_for", None)
        name = self.request.GET.get("name", None)

        if search_for is None or name is None:
            return Device.objects.none()

        if search_for == DeviceSearchForm.SearchFor.DEVICE:
            self.queryset = Device.objects.filter(
                group__owner=self.request.user, name__icontains=name
            )
        else:
            self.queryset = DeviceGroup.objects.filter(
                owner=self.request.user, name__icontains=name
            )

        queryset = self.queryset.all()

        ordering = self.ordering
        queryset = queryset.order_by(*ordering)

        return queryset

    def paginate_queryset(self, queryset, page_size):
        paginator = self.paginator_class(
            queryset,
            page_size,
            orphans=self.paginate_orphans,
            allow_empty_first_page=self.allow_empty,
        )
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == "last":
                page_number = paginator.num_pages
            elif page == "first":
                page_number = 1
            else:
                raise Http404(
                    _("Page is not “last”, nor can it be converted to an int.")
                )
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(
                _("Invalid page (%(page_number)s): %(message)s")
                % {"page_number": page_number, "message": str(e)}
            )

    def get_context_object_name(self, object_list):
        """Get the name of the item to be used in the context."""
        return self.context_object_name

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get the context for this view."""
        queryset = object_list if object_list is not None else self.get_queryset()
        page_size = self.paginate_by
        context_object_name = self.get_context_object_name(queryset)
        if queryset and queryset.count() > 0 and page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                queryset, page_size
            )
            context = {
                "paginator": paginator,
                "page_obj": page,
                "is_paginated": is_paginated,
                "object_list": queryset,
            }
        else:
            context = {
                "paginator": None,
                "page_obj": None,
                "is_paginated": False,
                "object_list": queryset,
            }

        context[context_object_name] = queryset
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            "initial": self.get_initial(),
            "prefix": self.get_prefix(),
            "data": self.request.GET,
        }

        return kwargs

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        form_context = dict(search_form=form)

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context.update(form_context)
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """Method is not allowed"""
        return HttpResponse(status=405)
