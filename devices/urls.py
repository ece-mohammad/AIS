from django.urls import include, path

from . import views 


app_name = "devices"


# -----------------------------------------------------------------------------
# Device Group URLs
# -----------------------------------------------------------------------------
group_edit_urlpatterns = [
    # details view
    path("details/", views.DeviceGroupDetailView.as_view(), name="group_details"),
    
    # TODO group devices
    # path("devices/", views.DeviceGroupDetailView.as_view(), name="group_details"),
    
    # edit view
    path("edit/", views.DeviceGroupEditView.as_view(), name="group_edit"),
    
    # delete view
    path("delete/", views.DeviceGroupDeleteView.as_view(), name="group_delete"),
]

group_urls = [
    
    # create view
    path("create/", views.DeviceGroupCreateView.as_view(), name="group_create"),
    
    # list view
    path("list/", views.DeviceGroupListView.as_view(), name="group_list"),
    
    # details, edit and remove views
    path("<slug:group_name>/", include(group_edit_urlpatterns)),
]

# -----------------------------------------------------------------------------
# Device URLs
# -----------------------------------------------------------------------------
device_edit_urls = [
    # details view
    path("details/", views.DeviceDetailView.as_view(), name="device_details"),
    
    # edit view
    path("edit/", views.DeviceEditView.as_view(), name="device_edit"),
    
    # delete view
    path("delete/", views.DeviceDeleteView.as_view(), name="device_delete"),
]

device_urls = [
    # create view
    path("create/", views.DeviceCreateView.as_view(), name="device_create"),
    
    # list view
    path("list/", views.DeviceListView.as_view(), name="device_list"),
    
    # details, edit, remove and deactivate views
    path("<slug:device_uid>/",  include(device_edit_urls)),
]

# -----------------------------------------------------------------------------
# Device Application URLs
# -----------------------------------------------------------------------------
urlpatterns = [
    path("", include(device_urls)),
    path("group/", include(group_urls)),
]
