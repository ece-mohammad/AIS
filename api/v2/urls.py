from django.db import router
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from.views import DeviceDataViewSet
from .views import (
    DeviceGroupListAPIView,
    DeviceGroupDetailsAPIView,
    DeviceListAPIView,
    DeviceDetailsAPIView,
    MemberDetailsAPIView,
)

# from.views import DeviceGroupAPIViewSet


"""
## API endpoints:

### /api/member/<username>/
- list member details


### /api/groups/
- list all member's groups


### /api/groups/<group_name>/
- list group details


### /api/groups/<group_name>/devices/
- list group's devices


### /api/devices/

- list all devices for current user
- create new device


### /api/devices/<device_uid>/

- get details for a device with given uid


### /api/devices/groups/

- list all device groups for current user
- create new device group


### /api/devices/groups/<group_name>/

- get details for a device group with given name


### /api/devices/<device_uid>/data/

- list all data for a device with given uid
- add new data to device


### /api/devices/<device_uid>/data/<data_id>/

- get details for a data with given device uid and data id

"""

app_name = "api"

devices_urls = [
    path("", DeviceListAPIView.as_view(), name="devices_list"),
    path("<slug:device_uid>/", DeviceDetailsAPIView.as_view(), name="device_details"),
]

device_groups_urls = [
    path("", DeviceGroupListAPIView.as_view(), name="groups_list"),
    path(
        "<slug:group_name>/", DeviceGroupDetailsAPIView.as_view(), name="group_details"
    ),
    # path("<slug:group_name>/devices/", include(devices_urls)),
]

version_1_url_patterns = [
    # member
    path(
        "members/<slug:username>/",
        MemberDetailsAPIView.as_view(),
        name="member_details",
    ),
]

version_2_url_patterns = []

urlpatterns = [
    # path("", include(router.urls)),
    path("v1/", include(version_1_url_patterns)),
    # device groups
    path("groups/", include(device_groups_urls)),
    # devices
    path("devices/", include(devices_urls)),
    # device data
    # path("data/<slug:device_uid>/", DeviceDataListAPIView.as_view(), name="device_data"),
    # path("devices/<slug:device_uid>/data/<int:pk>/", DeviceDataListAPIView.as_view(), name="data_details"),
]
