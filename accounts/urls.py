from django.urls import path, include

from . import views


app_name = "accounts"


password_reset_urlpatterns = [
    path("", views.MemberPasswordResetView.as_view(), name="password_reset"),
    path("done/", views.MemberPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("confirm/<slug:uidb64>/<slug:token>/", views.MemberPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("complete/", views.MemberPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

password_change_urlpatterns = [
    path("", views.MemberPasswordChangeView.as_view(), name="password_change"),
    path("done/", views.MemberPasswordChangeDoneView.as_view(), name="password_change_done"),
]

account_urlpatterns = [
    # user profile
    path("profile/", views.MemberProfileView.as_view(), name="profile"),
    
    # account deactivate
    path("deactivate/", views.MemberDeactivateView.as_view(), name="account_deactivate"),
    
    # account delete
    path("delete/", views.MemberDeleteView.as_view(), name="account_delete"),
]

urlpatterns = [
    
    # user signup
    path("signup/", views.MemberSignUpView.as_view(), name="signup"),
    
    # user login, logout
    path("login/", views.MemberLoginView.as_view(), name="login"),
    path("logout/", views.MemberLogoutView.as_view(), name="logout"),
    
    # user profile
    path("my_profile/", views.MemberOwnProfileView.as_view(), name="my_profile"),
    
    # password reset
    path("password_reset/", include(password_reset_urlpatterns)),
    
    # password change
    path("password_change/", include(password_change_urlpatterns)),
    
    # account patterns
    path("<slug:user_name>/", include(account_urlpatterns)),
]
