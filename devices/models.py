import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import Member

# Create your models here.


def initialize_device_data() -> models.Value:
    """
    Returns an  initializer for device data when the device is
    created. So that the field is not NULL or blank.

    :return JSONFiled None value through Value(None, JSONField())
    :rtype: models.Value
    """
    return models.Value(None, models.JSONField())


class DeviceGroup(models.Model):
    """
    Device group mode.

    +--------------------------------+
    |          Device Group          |
    +--------------------------------+
    | + name: SlugField[32]          |
    +--------------------------------+
    | + creation_date: DateTimeField |
    +--------------------------------+
    | + owner: ForeignKey(User)      |
    +--------------------------------+

    fields:
        - name: human readable name for the group,
        must be a non empty string and can contain spaces.
        - creation_date: date and time when was the group is created
        - owner: the user that created the group. Each group has one owner.
        The group can be modified only by the owner, or the system admin.

    A device group is used to interact devices in bulk. Any interaction that
    is applied to a device group, is applied to all devices within the group.
    A device group can have 0 or more devices. Each device can join
    at most one group at any given time.

    """

    name = models.SlugField(
        max_length=32,
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("device group name"),
        error_messages={
            "invalid": _(
                "Enter a valid device group name consisting of letters, numbers, underscores or hyphens."
            )
        },
    )

    description = models.TextField(
        max_length=256,
        verbose_name=_("device group description"),
        blank=True,
        null=False,
        default="",
    )

    creation_date = models.DateTimeField(
        verbose_name=_("creation date"),
        help_text=_("when was the group first created"),
        default=timezone.now,
    )

    owner = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        verbose_name=_("device group owner"),
    )

    def get_absolute_url(self):
        return reverse_lazy("devices:group_details", kwargs={"group_name": self.name})

    def __str__(self) -> str:
        return f"{self.name}"


class Device(models.Model):
    """
    Device model.

    +---------------------------------+
    |             Device              |
    +---------------------------------+
    | + name: SlugField[32]           |
    +---------------------------------+
    | + uid: UUIDField                |
    +---------------------------------+
    | + is_active: BooleanField       |
    +---------------------------------+
    | + date_added: DateTimeField     |
    +---------------------------------+
    | + group: ForeignKey(Group)      |
    +---------------------------------+

    fields:
        - name: human readable name for the device.
        - uid: globally unique ID for the device, automatically generated
        from the device name using uuid.UUID5(uuid.NAMESPACE_X500, device_name)
        - is_active: is the device enabled, True by default and set to False when
        the device is disabled.
        - date_added: when was the device added to the system.
        - group: device group the device belongs to.

    A device is a physical device that is connected to the system.
    It can be a sensor, a camera, a robot, or any other device that sends data,
    and optionally receives data.

    """

    # device properties
    uid = models.UUIDField(
        verbose_name="device unique ID",
        help_text="a globally unique ID for the device",
    )

    name = models.SlugField(
        max_length=32,
        verbose_name=_("device name"),
        help_text=_("human friendly device name"),
        error_messages={
            "invalid": _(
                "Enter a valid device name consisting of letters, numbers, underscores or hyphens."
            )
        },
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is device enabled"),
        help_text=_("is the device enabled"),
    )

    date_added = models.DateTimeField(
        verbose_name=_("date added"),
        default=timezone.now,
        help_text=_("when was the device added to the system"),
    )

    # relations
    group = models.ForeignKey(
        DeviceGroup, on_delete=models.CASCADE, verbose_name=_("device group")
    )

    def __str__(self):
        return f"{self.name}[{self.uid}]"

    @classmethod
    def generate_device_uid(cls, name: str) -> uuid.UUID:
        """Generate a device UID from the device name

        :param name: device name
        :type name: str
        :return: device UID
        :rtype: uuid.UUID: device UID
        """
        return uuid.uuid5(uuid.NAMESPACE_X500, name)

    def get_absolute_url(self):
        return reverse_lazy("devices:device_details", kwargs={"device_uid": self.uid})


class DeviceData(models.Model):
    """
    Device data model.

    +----------------------------+
    |        Device data         |
    +----------------------------+
    | + message: JSONField       |
    +----------------------------+
    | + date: DateTimeField      |
    +----------------------------+
    | + date: ForeignKey(Device) |
    +----------------------------+

    fields:
        - message: device data, JSON object that can contain any type of data.
        - date: when was the data received.
        - device: the device this data is associated with

    """

    DEFAULT_UPDATE_DATETIME = timezone.datetime(
        year=1900,
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=1,
        tzinfo=timezone.get_default_timezone(),
    )

    message = models.JSONField(
        encoder=DjangoJSONEncoder,
        verbose_name=_("data message"),
        default=initialize_device_data,
        null=False,
        blank=True,
    )

    date = models.DateTimeField(
        verbose_name=_("last update"),
        default=DEFAULT_UPDATE_DATETIME,
        help_text=_("when was the data received"),
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
    )
