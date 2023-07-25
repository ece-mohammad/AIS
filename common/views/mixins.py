from typing import *

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


class MemberLoginRequiredMixin(LoginRequiredMixin):
    """Custom login required mixin, redirects to 'accounts:login' page if not logged in"""
    login_url = reverse_lazy("accounts:login")


class AnonymousUserRequiredMixin(AccessMixin):
    """Verify that the current user is an anonymous user (not logged in)"""
    
    redirect_url: str|None = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)


class OwnerMemberRequiredMixin(AccessMixin):
    """Verify that the current user is the owner of the object"""
    
    def dispatch(self, request, *args, **kwargs):
        user_name = kwargs.get("user_name")
        user = request.user
        if user.username != user_name:
            self.permission_denied_message = "You do not have permission to access this page."
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
