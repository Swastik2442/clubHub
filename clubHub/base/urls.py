from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="baseIndex"),
    path("login/", views.login_view, name="loginPage"),
    path("signup/", views.signup_view, name="signupPage"),
    path("logout/", views.logout_view, name="logoutPage"),
    path("admin-page/", views.admin_view, name="adminPage"),
    path("admin-page/options/<int:opt>/", views.adminOptions, name="adminOptions"),
]