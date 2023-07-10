from typing import *

from django.contrib.auth import logout
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
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from common.views.mixins import (AnonymousUserRequiredMixin,
                                MemberLoginRequiredMixin,
                                OwnerMemberRequiredMixin)

from .forms import (MemberConfirmActionForm, MemberEditForm,
                    MemberPasswordChangeForm, MemberPasswordResetConfirmForm,
                    MemberSignUpForm)
from .models import Member

# Create your views here.


# -----------------------------------------------------------------------------
# ---------------------------- Registration Views -----------------------------
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# User Sign up view
# -----------------------------------------------------------------------------
class MemberSignUpView(AnonymousUserRequiredMixin, CreateView):
    """User signup view"""
    model = Member
    form_class = MemberSignUpForm
    template_name = "accounts/registration/signup.html"
    redirect_url = reverse_lazy("homepage")
    success_url = reverse_lazy("accounts:login")


class MemberDeactivateView(MemberLoginRequiredMixin, OwnerMemberRequiredMixin, UpdateView):
    """Deactivate member account"""
    model = Member
    form_class = MemberConfirmActionForm
    template_name = "accounts/registration/member_deactivate_confirm.html"
    success_url = reverse_lazy("homepage")
    slug_field = "username"
    slug_url_kwarg = "user_name"
    
    def form_valid(self, form: Any) -> HttpResponse:
        """Override form_valid to deactivate user account, 
        as MemberConfirmAction uses NoSaveMixin to not save the form
        
        Note: manually logout current user, instead of redirecting to logout page 
        because django will deprecate using GET method for logout, and it
        looks better that way
        """
        # deactivate current user
        self.request.user.is_active = False
        self.request.user.save()
        
        # logout current user
        logout(self.request)
        
        return super().form_valid(form)


class MemberDeleteView(MemberLoginRequiredMixin, OwnerMemberRequiredMixin, DeleteView):
    """Deactivate member account"""
    model = Member
    form_class = MemberConfirmActionForm
    template_name = "accounts/registration/member_delete_confirm.html"
    success_url = reverse_lazy("homepage")
    slug_field = "username"
    slug_url_kwarg = "user_name"
    
    def get_form_kwargs(self):
        """Override get_form_kwargs to pass instance to form,
        as DeleteView uses FormMixin to manage form creation,
        unlike ModelFromMixin which passes object instance to the form
        """
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_object()
        return kwargs


class MemberEditView(MemberLoginRequiredMixin, OwnerMemberRequiredMixin, UpdateView):
    model = Member
    form_class = MemberEditForm
    template_name = "accounts/registration/member_edit.html"
    slug_field = "username"
    slug_url_kwarg = "user_name"


# -----------------------------------------------------------------------------
# User login/logout views
# -----------------------------------------------------------------------------
class MemberLoginView(LoginView):
    """User login view"""
    template_name = "accounts/registration/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("homepage")


class MemberLogoutView(LogoutView):
    """User logout view"""
    template_name = "accounts/registration/logout.html"
    next_page = reverse_lazy("homepage")


# -----------------------------------------------------------------------------
# --------------------------- Member Profile Views ----------------------------
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# User profile view
# -----------------------------------------------------------------------------
class MemberProfileView(MemberLoginRequiredMixin, DetailView):
    """User profile view"""
    model = Member
    template_name = "accounts/profile.html"
    slug_field = "username"
    slug_url_kwarg = "user_name"
    context_object_name = "user"


class MemberOwnProfileView(MemberLoginRequiredMixin, View):
    """User's own profile"""
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return HttpResponseRedirect(reverse_lazy("accounts:profile", kwargs={"user_name": request.user.username}))


# -----------------------------------------------------------------------------
# ------------------------- Password Management Views -------------------------
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# User password reset views
# -----------------------------------------------------------------------------
class MemberPasswordResetView(AnonymousUserRequiredMixin, PasswordResetView):
    """User password reset view"""
    template_name = "accounts/registration/password_reset_form.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    redirect_url = reverse_lazy("homepage")
    email_template_name = "accounts/registration/password_reset_email.html"
    subject_template_name = "accounts/registration/password_reset_subject.txt"


class MemberPasswordResetDoneView(AnonymousUserRequiredMixin, PasswordResetDoneView):
    """User password reset done view"""
    template_name = "accounts/registration/password_reset_done.html"


class MemberPasswordResetConfirmView(AnonymousUserRequiredMixin, PasswordResetConfirmView):
    """User password reset confirm view"""
    form_class = MemberPasswordResetConfirmForm
    template_name = "accounts/registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")
    title = "Password Reset Confirm"


class MemberPasswordResetCompleteView(AnonymousUserRequiredMixin, PasswordResetCompleteView):
    """User password reset complete view"""
    template_name = "accounts/registration/password_reset_complete.html"
    redirect_url = reverse_lazy("homepage")


# -----------------------------------------------------------------------------
# User password change views
# -----------------------------------------------------------------------------
class MemberPasswordChangeView(PasswordChangeView):
    """User password change view"""
    form_class = MemberPasswordChangeForm
    template_name = "accounts/registration/password_change_form.html"
    login_url = reverse_lazy("accounts:login")
    success_url = reverse_lazy("accounts:password_change_done")


class MemberPasswordChangeDoneView(PasswordChangeDoneView):
    """User password change done view"""
    template_name = "accounts/registration/password_change_done.html"
    login_url = reverse_lazy("accounts:login")

