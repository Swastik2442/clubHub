from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="baseIndex"),
    path("admin-page/", views.admin_view, name="adminPage"),
    path("login/", views.login_view, name="loginPage"),
    path("signup/", views.signup_view, name="signupPage"),
]