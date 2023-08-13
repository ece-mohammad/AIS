from typing import *

from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import authentication, generics, permissions, status, views
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Member
from api.v1.serializers import (
    DeviceDataSerializer,
    DeviceGroupSerializer,
    DeviceSerializer,
    MemberSerializer,
)
from devices.models import Device, DeviceData, DeviceGroup
from devices.tests import device


# -----------------------------------------------------------------------------
# Base classes
# -----------------------------------------------------------------------------
class IsObjectOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view and edit it.
    """

    def has_permission(self, request, view):
        user = request.user
        url_username = view.kwargs.get("username")
        return user.username == url_username


class AuthenticatedUserAPIView(views.APIView):
    # required authentication
    authentication_classes = [
        authentication.SessionAuthentication,
    ]

    # required permission
    permission_classes = [
        permissions.IsAuthenticated,
        IsObjectOwner,
    ]

    def get_serializer_context(self):
        return dict(request=self.request)

# -----------------------------------------------------------------------------
# Device Groups
# -----------------------------------------------------------------------------
class MemberDetailsAPIView(generics.RetrieveAPIView, AuthenticatedUserAPIView):
    """
    Retrieve a member instance
    """

    serializer_class = MemberSerializer

    def get_object(self):
        username = self.kwargs["username"]
        query_filters = Q(username=username)
        return get_object_or_404(Member, query_filters)


# -----------------------------------------------------------------------------
# Device Groups
# -----------------------------------------------------------------------------
class DeviceGroupListAPIView(generics.ListCreateAPIView, AuthenticatedUserAPIView):
    """
    List all device groups, or create a new device group
    """

    serializer_class = DeviceGroupSerializer
    queryset = DeviceGroup.objects.all()

    def filter_queryset(self, queryset):
        username = self.kwargs["username"]
        query_filters = Q(owner__username__iexact=username)
        return queryset.filter(query_filters)

    def get_object(self):
        username = self.kwargs["username"]
        group_name = self.kwargs["group_name"]
        query_filters = Q(name=group_name) & Q(owner__username=username)
        return get_object_or_404(DeviceGroup, query_filters)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

#     def get(self, request: Request, username: str, format=None) -> Response:
#         """Get list of all device groups"""
#         query_filters = Q(owner__username=username)
#         device_groups = get_list_or_404(DeviceGroup, query_filters)
#         serializer = DeviceGroupSerializer(
#             instance=device_groups, many=True, context={"request": request}
#         )
#         return Response(serializer.data)
# 
#     def post(self, request: Request, username: str, format=None) -> Response:
#         """A new device group"""
#         owner = self.request.user
#         group_data = request.data
#         serializer = DeviceGroupSerializer(
#             data=group_data, context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save(owner=owner)
#         return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class DeviceGroupDetailsAPIView(generics.RetrieveUpdateDestroyAPIView, AuthenticatedUserAPIView):
    """
    Retrieve a device group instance
    """

    serializer_class = DeviceGroupSerializer

    def get_object(self):
        username = self.kwargs["username"]
        group_name = self.kwargs["group_name"]
        query_filters = Q(name__iexact=group_name) & Q(owner__username__iexact=username)
        return get_object_or_404(DeviceGroup, query_filters)

    # def get_object(self, username: str, group_name: str) -> DeviceGroup:
    #     query_filters = Q(name=group_name) & Q(owner__username=username)
    #     device_group = get_object_or_404(DeviceGroup, query_filters)
    #     return device_group
    # 
    # def get(
    #     self, request: Request, username: str, group_name: str, format=None
    # ) -> Response:
    #     """Get details for a device group with given name"""
    #     device_group = self.get_object(username, group_name)
    #     serializer = DeviceGroupSerializer(
    #         instance=device_group, context={"request": request}
    #     )
    #     return Response(data=serializer.data)
    # 
    # def put(
    #     self, request: Request, username: str, group_name: str, format=None
    # ) -> Response:
    #     device_group = self.get_object(username, group_name)
    #     serializer = DeviceGroupSerializer(
    #         instance=device_group, data=request.data, context={"request": request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(data=serializer.data)
    # 
    # def patch(
    #     self, request: Request, username: str, group_name: str, format=None
    # ) -> Response:
    #     device_group = self.get_object(username, group_name)
    #     serializer = DeviceGroupSerializer(
    #         instance=device_group,
    #         data=request.data,
    #         context={"request": request},
    #         partial=True,
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(data=serializer.data)
    # 
    # def delete(
    #     self, request: Request, username: str, group_name: str, format=None
    # ) -> Response:
    #     device_group = self.get_object(username, group_name)
    #     device_group.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------
# Devices
# -----------------------------------------------------------------------------
class DeviceListAPIView(generics.ListCreateAPIView, AuthenticatedUserAPIView):
    """
    List all devices for current user
    """
    
    serializer_class = DeviceSerializer
    queryset = Device.objects.all()
    
    def filter_queryset(self, queryset):
        username = self.kwargs["username"]
        group_name = self.kwargs["group_name"]
        query_filters = Q(group__owner__username__iexact=username) & Q(group__name__iexact=group_name)
        return queryset.filter(query_filters)
    
    def perform_create(self, serializer):
        username = self.kwargs["username"]
        group_name = self.kwargs["group_name"]
        group_query = Q(owner__username=username) & Q(name=group_name)
        group = get_object_or_404(DeviceGroup, group_query)
        serializer.save(group=group)

#    def get(
#        self, request: Request, username: str, group_name: str, format=None
#    ) -> Response:
#        """Get list of all devices"""
#        query_filters = Q(group__owner__username=username) & Q(group__name=group_name)
#        devices = get_list_or_404(Device, query_filters)
#        serializer = DeviceSerializer(
#            instance=devices, many=True, context={"request": request}
#        )
#        return Response(data=serializer.data)
#
#    def post(
#        self, request: Request, username: str, group_name: str, format=None
#    ) -> Response:
#        """Add a new device"""
#        user = self.request.user
#        group_query = Q(owner__username=username) & Q(name=group_name)
#        group = get_object_or_404(DeviceGroup, group_query)
#        device_data = request.data
#        serializer = DeviceSerializer(data=device_data, context={"request": request})
#        serializer.is_valid(raise_exception=True)
#        serializer.save(group=group)
#        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class DeviceDetailsAPIView(generics.RetrieveUpdateDestroyAPIView, AuthenticatedUserAPIView):
    """
    Retrieve a device instance
    """

    serializer_class = DeviceSerializer

    def get_object(self):
        username = self.kwargs["username"]
        group_name = self.kwargs["group_name"]
        device_uid = self.kwargs["device_uid"]
        query_filters = Q(uid=device_uid) & Q(group__name=group_name) & Q(group__owner__username=username)
        return get_object_or_404(Device, query_filters)

    def perform_update(self, serializer):
        username = self.kwargs["username"]
        group_name = self.kwargs["group_name"]
        group_query = Q(owner__username=username) & Q(name=group_name)
        group = get_object_or_404(DeviceGroup, group_query)
        serializer.save(group=group)

    # def get_object(self, username: str, group_name: str, device_uid: str) -> Device:
    #     query_filters = (
    #         Q(uid=device_uid)
    #         & Q(group__name=group_name)
    #         & Q(group__owner__username=username)
    #     )
    #     device = get_object_or_404(Device, query_filters)
    #     return device

    # def get(
    #     self,
    #     request: Request,
    #     username: str,
    #     group_name: str,
    #     device_uid: str,
    #     format=None,
    # ) -> Response:
    #     """Get details for a device with given uid"""
    #     device = self.get_object(username, group_name, device_uid)
    #     serializer = DeviceSerializer(instance=device, context={"request": request})
    #     return Response(data=serializer.data)

    # def put(
    #     self,
    #     request: Request,
    #     username: str,
    #     group_name: str,
    #     device_uid: str,
    #     format=None,
    # ) -> Response:
    #     device = self.get_object(username, group_name, device_uid)
    #     serializer = DeviceSerializer(
    #         instance=device,
    #         data=request.data,
    #         context={"request": request},
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(group=device.group)
    #     return Response(data=serializer.data)

    # def patch(
    #     self,
    #     request: Request,
    #     username: str,
    #     group_name: str,
    #     device_uid: str,
    #     format=None,
    # ) -> Response:
    #     device = self.get_object(username, group_name, device_uid)
    #     serializer = DeviceSerializer(
    #         instance=device,
    #         data=request.data,
    #         context={"request": request},
    #         partial=True,
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(group=device.group)
    #     return Response(data=serializer.data)

    # def delete(
    #     self,
    #     request: Request,
    #     username: str,
    #     group_name: str,
    #     device_uid: str,
    #     format=None,
    # ) -> Response:
    #     device = self.get_object(username, group_name, device_uid)
    #     device.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------
# Device Data
# -----------------------------------------------------------------------------
class DeviceDataListAPIView(generics.ListCreateAPIView, AuthenticatedUserAPIView):
    """
    List all device's data, or create new data
    """

    serializer_class = DeviceDataSerializer
    queryset = DeviceData.objects.all()
    
    def filter_queryset(self, queryset):
        username = self.kwargs["username"]
        group_name = self.kwargs["group_name"]
        device_uid = self.kwargs["device_uid"]
        query_filters = (
            Q(uid=device_uid)
            & Q(group__name=group_name)
            & Q(group__owner__username=username)
        )
        device = get_object_or_404(Device, query_filters)
        return queryset.filter(device=device)

    def perform_create(self, serializer):
        device_uid = self.kwargs["device_uid"]
        device = get_object_or_404(Device, uid=device_uid)
        serializer.save(device=device)

#    def get(
#        self,
#        request: Request,
#        username: str,
#        group_name: str,
#        device_uid: str,
#        format=None,
#    ) -> Response:
#        """Get list of all device's data"""
#        query_filters = (
#            Q(uid=device_uid)
#            & Q(group__name=group_name)
#            & Q(group__owner__username=username)
#        )
#
#        device = get_object_or_404(Device, query_filters)
#        data_list = device.devicedata_set.all()
#        serializer = DeviceDataSerializer(
#            instance=data_list, many=True, context={"request": request}
#        )
#        return Response(data=serializer.data)
#
#    def post(
#        self,
#        request: Request,
#        username: str,
#        group_name: str,
#        device_uid: str,
#        format=None,
#    ) -> Response:
#        """Add data to device"""
#        query_filters = Q(uid=device_uid)
#        device = get_object_or_404(Device, query_filters)
#        device_data = request.data
#        serializer = DeviceDataSerializer(
#            data=device_data, context={"request": request}
#        )
#        serializer.is_valid(raise_exception=True)
#        serializer.save(device=device)
#        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeviceDataDetailsAPIView(generics.RetrieveUpdateDestroyAPIView, AuthenticatedUserAPIView):
    """
    Retrieve a device data instance
    """

    serializer_class = DeviceDataSerializer

    def get_object(self):
        username = self.kwargs["username"]
        group_name = self.kwargs["group_name"]
        device_uid = self.kwargs["device_uid"]
        data_id = self.kwargs["data_id"]
        query_filters = (
            Q(device__uid=device_uid)
            & Q(device__group__name__iexact=group_name)
            & Q(device__group__owner__username__iexact=username)
            & Q(id=data_id)
        )
        return get_object_or_404(DeviceData, query_filters)


    # def get_object(
    #     self, username: str, group_name: str, device_uid: str, data_id: int
    # ) -> Device:
    #     query_filters = (
    #         Q(device__uid=device_uid)
    #         & Q(device__group__name=group_name)
    #         & Q(device__group__owner__username=username)
    #         & Q(id=data_id)
    #     )
    #     device_data = get_object_or_404(DeviceData, query_filters)
    #     return device_data

    # def get(
    #     self,
    #     request: Request,
    #     username: str,
    #     group_name: str,
    #     device_uid: str,
    #     data_id: int,
    #     format=None,
    # ) -> Response:
    #     """Get list of all device's data"""
    #     device_data = self.get_object(username, group_name, device_uid, data_id)
    #     serializer = DeviceDataSerializer(
    #         instance=device_data, context={"request": request}
    #     )
    #     return Response(data=serializer.data)

    # def put(
    #     self,
    #     request: Request,
    #     username: str,
    #     group_name: str,
    #     device_uid: str,
    #     data_id: int,
    #     format=None,
    # ) -> Response:
    #     device_data = self.get_object(username, group_name, device_uid, data_id)
    #     serializer = DeviceDataSerializer(
    #         instance=device_data,
    #         data=request.data,
    #         context={"request": request},
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(data=serializer.data)

    # def patch(
    #     self,
    #     request: Request,
    #     username: str,
    #     group_name: str,
    #     device_uid: str,
    #     data_id: int,
    #     format=None,
    # ) -> Response:
    #     device_data = self.get_object(username, group_name, device_uid, data_id)
    #     serializer = DeviceDataSerializer(
    #         instance=device_data,
    #         data=request.data,
    #         context={"request": request},
    #         partial=True,
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(data=serializer.data)

    # def delete(
    #     self,
    #     request: Request,
    #     username: str,
    #     group_name: str,
    #     device_uid: str,
    #     data_id: int,
    #     format=None,
    # ) -> Response:
    #     device_data = self.get_object(username, group_name, device_uid, data_id)
    #     device_data.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
