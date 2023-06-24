from typing import *

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView,
                                        PasswordChangeDoneView,
                                        PasswordChangeView,
                                        PasswordResetCompleteView,
                                        PasswordResetConfirmView,
                                        PasswordResetDoneView,
                                        PasswordResetView)
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView

from .forms import (MemberEditForm, MemberPasswordChangeForm,
                    MemberPasswordResetForm, MemberSignUpForm)
from .models import Member

# Create your views here.

# -----------------------------------------------------------------------------
# Helper classes
# -----------------------------------------------------------------------------
class AnonymousUserMixin(AccessMixin):
    """Verify that the current user is an anonymous user (not logged in)"""
    
    redirect_url: str|None = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)


# -----------------------------------------------------------------------------
# User Sign up view
# -----------------------------------------------------------------------------
class UserSignUpView(AnonymousUserMixin, CreateView):
    """User signup view"""
    model = Member
    form_class = MemberSignUpForm
    template_name = "accounts/registration/signup.html"
    redirect_url = reverse_lazy("homepage")
    success_url = reverse_lazy("accounts:login")


# -----------------------------------------------------------------------------
# User login/logout views
# -----------------------------------------------------------------------------
class UserLoginView(LoginView):
    """User login view"""
    template_name = "accounts/registration/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("homepage")


class UserLogoutView(LogoutView):
    """User logout view"""
    template_name = "accounts/registration/logout.html"
    next_page = reverse_lazy("homepage")


# -----------------------------------------------------------------------------
# User profile view
# -----------------------------------------------------------------------------
class UserProfileView(LoginRequiredMixin, DetailView):
    """User profile view"""
    model = Member
    template_name = "accounts/profile.html"
    login_url = reverse_lazy("accounts:login")
    slug_field = "username"
    slug_url_kwarg = "user_name"
    context_object_name = "user"


class UserOwnProfileView(LoginRequiredMixin, View):
    """User's own profile"""
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return HttpResponseRedirect(reverse_lazy("accounts:profile", kwargs={"user_name": request.user.username}))


# -----------------------------------------------------------------------------
# User password reset views
# -----------------------------------------------------------------------------
class UserPasswordResetView(AnonymousUserMixin, PasswordResetView):
    """User password reset view"""
    template_name = "accounts/registration/password_reset_form.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    redirect_url = reverse_lazy("homepage")
    email_template_name = "accounts/registration/password_reset_email.html"
    subject_template_name = "accounts/registration/password_reset_subject.txt"


class UserPasswordResetDoneView(AnonymousUserMixin, PasswordResetDoneView):
    """User password reset done view"""
    template_name = "accounts/registration/password_reset_done.html"


class UserPasswordResetConfirmView(AnonymousUserMixin, PasswordResetConfirmView):
    """User password reset confirm view"""
    template_name = "accounts/registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class UserPasswordResetCompleteView(AnonymousUserMixin, PasswordResetCompleteView):
    """User password reset complete view"""
    template_name = "accounts/registration/password_reset_complete.html"
    redirect_url = reverse_lazy("homepage")


# -----------------------------------------------------------------------------
# User password change views
# -----------------------------------------------------------------------------
class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """User password change view"""
    template_name = "accounts/registration/password_change.html"
    login_url = reverse_lazy("accounts:login")
    redirect_url = reverse_lazy("homepage")
    success_url = reverse_lazy("accounts:password_change_done")


class UserPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """User password change done view"""
    template_name = "accounts/registration/password_change_done.html"
    redirect_url = reverse_lazy("homepage")
    login_url = reverse_lazy("accounts:login")

