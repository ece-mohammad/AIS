from django.urls import path, include

from . import views


app_name = "accounts"


password_reset_urlpatterns = [
    path("", views.UserPasswordResetView.as_view(), name="password_reset"),
    path("done/", views.UserPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("confirm/<slug:uidb64>/<slug:token>/", views.UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("complete/", views.UserPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

password_change_urlpatterns = [
    path("", views.UserPasswordChangeView.as_view(), name="password_change"),
    path("done/", views.UserPasswordChangeDoneView.as_view(), name="password_change_done"),
]

urlpatterns = [
    
    # user signup
    path("signup/", views.UserSignUpView.as_view(), name="signup"),
    
    # user login, logout
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    
    # user profile
    path("my_profile/", views.UserOwnProfileView.as_view(), name="my_profile"),
    path("profile/<slug:user_name>/", views.UserProfileView.as_view(), name="profile"),
    
    # # password reset
    path("password_reset/", include(password_reset_urlpatterns)),
    
    # # password change
    path("password_change/", include(password_change_urlpatterns)),
]
