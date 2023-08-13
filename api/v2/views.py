from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils import timezone
from rest_framework import (
    authentication,
    generics,
    permissions,
    status,
    views,
    viewsets,
)
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Member
from api.v2.serializers import (
    DeviceDataSerializer,
    DeviceGroupSerializer,
    DeviceSerializer,
    MemberSerializer,
)
from devices.models import Device, DeviceData, DeviceGroup


# -----------------------------------------------------------------------------
# Base classes
# -----------------------------------------------------------------------------
class AuthenticatedUserAPIView(views.APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# -----------------------------------------------------------------------------
# Device Groups
# -----------------------------------------------------------------------------
class MemberDetailsAPIView(AuthenticatedUserAPIView):
    """
    Retrieve a member instance
    """

    def get(self, request: Request, username: str, format=None) -> Response:
        """Get details for current user"""
        member = get_object_or_404(Member, username=username)

        if member != request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"detail": "You do not have permission to perform this action."},
            )

        serializer = MemberSerializer(member, context={"request": request})
        return Response(serializer.data)


# -----------------------------------------------------------------------------
# Device Groups
# -----------------------------------------------------------------------------
class DeviceGroupListAPIView(AuthenticatedUserAPIView):
    """
    List all device groups, or create a new device group
    """

    def get(self, request: Request, format=None) -> Response:
        """Get list of all device groups"""
        owner = request.user
        serializer = DeviceGroupSerializer(
            DeviceGroup.objects.filter(owner=owner),
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request: Request, format=None) -> Response:
        """A new device group"""
        owner = self.request.user
        group_data = request.data
        serializer = DeviceGroupSerializer(
            data=group_data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(owner_id=owner.id, creation_date=timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceGroupDetailsAPIView(AuthenticatedUserAPIView):
    """
    Retrieve a device group instance
    """

    def get(self, request: Request, group_name: str, format=None) -> Response:
        """Get details for a device group with given name"""
        owner = request.user
        device_group = get_object_or_404(DeviceGroup, name=group_name, owner=owner)
        serializer = DeviceGroupSerializer(device_group, context={"request": request})
        return Response(serializer.data)


# -----------------------------------------------------------------------------
# Devices
# -----------------------------------------------------------------------------
class DeviceListAPIView(AuthenticatedUserAPIView):
    """
    List all devices for current user
    """

    def get(self, request: Request, format=None) -> Response:
        """Get list of all devices"""
        owner = request.user
        serializer = DeviceSerializer(
            Device.objects.filter(group__owner=owner),
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class DeviceDetailsAPIView(AuthenticatedUserAPIView):
    """
    Retrieve a device instance
    """

    def get(self, request: Request, device_uid: str, format=None) -> Response:
        """Get details for a device with given uid"""
        owner = request.user
        device = get_object_or_404(Device, uid=device_uid, group__owner=owner)
        serializer = DeviceSerializer(device, context={"request": request})
        return Response(serializer.data)


# -----------------------------------------------------------------------------
# Device Data
# -----------------------------------------------------------------------------
class DeviceDataListAPIView(AuthenticatedUserAPIView):
    """
    List all device's data, or create new data
    """

    def get(self, request: Request, device_uid: str, format=None) -> Response:
        """Get list of all device's data"""
        device_data = DeviceData.objects.filter(
            device__uid=device_uid, device__group__owner=self.request.user
        )
        serializer = DeviceDataSerializer(
            device_data, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request: Request, device_uid: str, format=None) -> Response:
        """Add data to device"""
        device = get_object_or_404(
            Device, uid=device_uid, group__owner=self.request.user
        )
        device_data = request.data
        device_data["device_id"] = device.id
        serializer = DeviceDataSerializer(
            data=device_data, device_uid=device_uid, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
