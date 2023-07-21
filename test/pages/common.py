
""" 
Provides common pages with their respective title, template name, 
view name, and reversed url. Each page is an instances of Page dataclass.

Pages:
------
    - HomePage
    - SignUp
    - Login
    - LogOut
    - MemberProfile
    - PasswordReset
    - PasswordResetDone
    - PasswordResetConfirm
    - PasswordResetComplete
    - PasswordChange
    - PasswordChangeDone
    - MemberDeactivate
    - MemberDelete
    - MemberEdit`

"""
# -------------------------------------------------------------------------
#
# -------------------------------------------------------------------------

from typing import *
from dataclasses import dataclass
from string import Template
from django.urls import reverse_lazy


@dataclass(slots=True, frozen=True)
class Page:
    """
    Page dataclass to hold page's title, template name, view name, and url.
    The class is set with dataclass decorator (frozen=True) to make it 
    immutable and hashable.
    
    :attr title: Page's title
    :type title: str
    :attr template_name: Page's template name
    :type template_name: str
    :attr view_name: Page's view name
    :type view_name: str
    :attr _url: Page's url (using django's reverse_lazy), default is ""
    :type _url: str
    :attr _kw_url: Page's url with keyword arguments (using python's string.Template), default is ""
    :type _kw_url: str
    """
    title: str
    template_name: str
    view_name: str
    _url: str = ""
    _kw_url: str = ""
    kwargs: Tuple[str] = None

    def get_url(self, **kwargs) -> str:
        if self._kw_url == "":
            return self._url
        
        url_template = Template(self._kw_url)
        if not url_template.get_identifiers():
            return self._url 
        
        url_vars = {k:kwargs[k] for k in kwargs} if kwargs else {}
        return url_template.substitute(url_vars)


HomePage: Final[Page] = Page(
    title="Dashboard",
    template_name="dashboard/dashboard.html",
    view_name="homepage",
    _url=reverse_lazy("homepage"),
)

# -----------------------------------------------------------------------------
# Registration pages
# -----------------------------------------------------------------------------
SignUp: Final[Page] = Page(
    title="Sign Up",
    template_name="accounts/registration/signup.html",
    view_name="accounts:signup",
    _url=reverse_lazy("accounts:signup"),
)

LogIn: Final[Page] = Page(
    title="Log In",
    template_name="accounts/registration/login.html",
    view_name="accounts:login",
    _url=reverse_lazy("accounts:login"),
)

LogOut: Final[Page] = Page(
    title="Logout",
    template_name=None,
    view_name="accounts:logout",
    _url=reverse_lazy("accounts:logout"),
)

MemberProfile: Final[Page] = Page(
    title="Profile",
    template_name="accounts/profile.html",
    view_name="accounts:profile",
    _kw_url="/accounts/${username}/profile/",
    kwargs=("username",),
)

PasswordReset: Final[Page] = Page(
    title="Password Reset",
    template_name="accounts/registration/password_reset_form.html",
    view_name="accounts:password_reset",
    _url=reverse_lazy("accounts:password_reset"),
)

PasswordResetDone: Final[Page] = Page(
    title="Password Reset Done",
    template_name="accounts/registration/password_reset_done.html",
    view_name="accounts:password_reset_done",
    _url=reverse_lazy("accounts:password_reset_done"),
)

PasswordResetConfirm: Final[Page] = Page(
    title="Password Reset Confirm",
    template_name="accounts/registration/password_reset_confirm.html",
    view_name="accounts:password_reset_confirm",
    _url=reverse_lazy("accounts:password_reset_confirm"),
)

PasswordResetComplete: Final[Page] = Page(
    title="Password Reset Complete",
    template_name="accounts/registration/password_reset_complete.html",
    view_name="accounts:password_reset_complete",
    _url=reverse_lazy("accounts:password_reset_complete"),
)

PasswordChange: Final[Page] = Page(
    title="Password Change",
    template_name="accounts/registration/password_change_form.html",
    view_name="accounts:password_change",
    _url=reverse_lazy("accounts:password_change"),
)

PasswordChangeDone: Final[Page] = Page(
    title="Password Changed",
    template_name="accounts/registration/password_change_done.html",
    view_name="accounts:password_change_done",
    _url=reverse_lazy("accounts:password_change_done"),
)

MemberDeactivate: Final[Page] = Page(
    title="Deactivate Account",
    template_name="accounts/registration/member_deactivate_confirm.html",
    view_name="accounts:account_deactivate",
    _kw_url="/accounts/${username}/deactivate/",
    kwargs=("username",),
)

MemberDelete: Final[Page] = Page(
    title="Delete Account",
    template_name="accounts/registration/member_delete_confirm.html",
    view_name="accounts:account_delete",
    _kw_url="/accounts/${username}/delete/",
    kwargs=("username",),
)

MemberEdit: Final[Page] = Page(
    title="Edit Profile",
    template_name="accounts/registration/member_edit.html",
    view_name="accounts:profile_edit",
    _kw_url="/accounts/${username}/edit/",
    kwargs=("username",),
)

# -----------------------------------------------------------------------------
# Device Group pages
# -----------------------------------------------------------------------------
DeviceGroupCreate: Final[Page] = Page(
    title="Create Device Group",
    template_name="devices/group/create.html",
    view_name="devices:group_create",
    _url=reverse_lazy("devices:group_create"),
)

DeviceGroupDetails: Final[Page] = Page(
    title="Device Group Details",
    template_name="devices/group/details.html",
    view_name="devices:group_details",
    _kw_url="/device/group/${group_name}/details/",
    kwargs=("group_name",),
)

DeviceGroupEdit: Final[Page] = Page(
    title="Edit Device Group",
    template_name="devices/group/edit.html",
    view_name="devices:group_edit",
    _kw_url="/device/group/${group_name}/edit/",
    kwargs=("group_name",),
)

DeviceGroupDelete: Final[Page] = Page(
    title="Delete Device Group",
    template_name="devices/group/delete.html",
    view_name="devices:group_delete",
    _kw_url="/device/group/${group_name}/delete/",
    kwargs=("group_name",),
)

DeviceGroupList: Final[Page] = Page(
    title="Device Groups",
    template_name="devices/group/list.html",
    view_name="devices:group_list",
    _url=reverse_lazy("devices:group_list"),
)

# -----------------------------------------------------------------------------
# Device pages
# -----------------------------------------------------------------------------
DeviceCreate: Final[Page] = Page(
    title="Create Device",
    template_name="devices/device/create.html",
    view_name="devices:device_create",
    _url=reverse_lazy("devices:device_create"),
)

DeviceList: Final[Page] = Page(
    title="Device List",
    template_name="devices/device/list.html",
    view_name="devices:device_list",
    _url=reverse_lazy("devices:device_list"),
)

DeviceDetails: Final[Page] = Page(
    title="Device Details",
    template_name="devices/device/details.html",
    view_name="devices:device_details",
    _kw_url="/device/${device_uid}/details/",
    kwargs=("device_uid",),
)

DeviceEdit: Final[Page] = Page(
    title="Edit Device",
    template_name="devices/device/edit.html",
    view_name="devices:device_edit",
    _kw_url="/device/${device_uid}/edit/",
    kwargs=("device_name",),
)

DeviceDelete: Final[Page] = Page(
    title="Delete Device",
    template_name="devices/device/delete.html",
    view_name="devices:device_delete",
    _kw_url="/device/${device_uid}/delete/",
    kwargs=("device_name",),
)

# -----------------------------------------------------------------------------
# Device Data pages
# -----------------------------------------------------------------------------
DeviceDataDetails: Final[Page] = Page(
    title="Device Data",
    template_name="devices/data/details.html",
    view_name="devices:data_details",
    _kw_url="/device/data/${data_id}/",
    kwargs=("data_id",),
)

DeviceDataList: Final[Page] = Page(
    title="Data List",
    template_name="devices/data/list.html",
    view_name="devices:data_list",
    _url=reverse_lazy("devices:data_list"),
)

DeviceDataHistory: Final[Page] = Page(
    title="Device Data",
    template_name="devices/device/data_history.html",
    view_name="devices:device_data_list",
    _kw_url="/device/${device_uid}/data/",
    kwargs=("device_uid"),
)