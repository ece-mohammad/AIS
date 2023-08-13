from django.urls import include, path

from api.v1.views import (
    DeviceDataDetailsAPIView,
    DeviceDataListAPIView,
    DeviceDetailsAPIView,
    DeviceGroupDetailsAPIView,
    DeviceGroupListAPIView,
    DeviceListAPIView,
    MemberDetailsAPIView,
)

"""
## API endpoints:

- /api/v1/member/<str:username>/
- /api/v1/member/<str:username>/groups/
- /api/v1/member/<str:username>/groups/<str:group_name>/
- /api/v1/member/<str:username>/groups/<str:group_name>/devices/
- /api/v1/member/<str:username>/groups/<str:group_name>/devices/<str:device_name>/
- /api/v1/member/<str:username>/groups/<str:group_name>/devices/<str:device_name>/data/
- /api/v1/member/<str:username>/groups/<str:group_name>/devices/<str:device_name>/data/<str:data_id>/

"""

namespace = "v1"

members_urlpatterns = [
    # member details
    path("<str:username>/", MemberDetailsAPIView.as_view(), name="member_details"),
    # device groups
    path(
        "<str:username>/groups/", DeviceGroupListAPIView.as_view(), name="groups_list"
    ),
    path(
        "<str:username>/groups/<str:group_name>/",
        DeviceGroupDetailsAPIView.as_view(),
        name="group_details",
    ),
    # devices
    path(
        "<str:username>/groups/<str:group_name>/devices/",
        DeviceListAPIView.as_view(),
        name="devices_list",
    ),
    path(
        "<str:username>/groups/<str:group_name>/devices/<str:device_uid>/",
        DeviceDetailsAPIView.as_view(),
        name="device_details",
    ),
    # data
    path(
        "<str:username>/groups/<str:group_name>/devices/<str:device_uid>/data/",
        DeviceDataListAPIView.as_view(),
        name="data_list",
    ),
    path(
        "<str:username>/groups/<str:group_name>/devices/<str:device_uid>/data/<int:data_id>/",
        DeviceDataDetailsAPIView.as_view(),
        name="data_details",
    ),
]


urlpatterns = [
    # members
    path("members/", include(members_urlpatterns)),
]
