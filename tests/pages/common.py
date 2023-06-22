
""" 
Provides common pages with their respective title, template name, 
view name, and reversed url. Each page is an instances of Page dataclass.

Pages:
------
    - HomePage
    - SignUp
    - Login

"""
# -------------------------------------------------------------------------
#
# -------------------------------------------------------------------------

from typing import *
from dataclasses import dataclass

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
    :attr url: Page's url
    :type url: str
    """
    title: str
    template_name: str
    view_name: str
    url: str


HomePage: Final[Page] = Page(
    title="Dashboard",
    template_name="dashboard/dashboard.html",
    view_name="homepage",
    url=reverse_lazy("homepage"),
)

SignUp: Final[Page] = Page(
    title="Sign Up",
    template_name="accounts/registration/signup.html",
    view_name="accounts:signup",
    url=reverse_lazy("accounts:signup"),
)

LogIn: Final[Page] = Page(
    title="Login",
    template_name="accounts/registration/login.html",
    view_name="accounts:login",
    url=reverse_lazy("accounts:login"),
)

LogOut: Final[Page] = Page(
    title="Logout",
    template_name=None,
    view_name="accounts:logout",
    url=reverse_lazy("accounts:logout"),
)

PasswordReset = Page(
    title="Password Reset",
    template_name="accounts/registration/password_reset_form.html",
    view_name="accounts:password_reset",
    url=reverse_lazy("accounts:password_reset"),
)

PasswordResetDone = Page(
    title="Password Reset Done",
    template_name="accounts/registration/password_reset_done.html",
    view_name="accounts:password_reset_done",
    url=reverse_lazy("accounts:password_reset_done"),
)

PasswordResetConfirm = Page(
    title="Password Reset Confirm",
    template_name="accounts/registration/password_reset_confirm.html",
    view_name="accounts:password_reset_confirm",
    url=reverse_lazy("accounts:password_reset_confirm"),
)

PasswordResetComplete = Page(
    title="Password Reset Complete",
    template_name="accounts/registration/password_reset_complete.html",
    view_name="accounts:password_reset_complete",
    url=reverse_lazy("accounts:password_reset_complete"),
)
