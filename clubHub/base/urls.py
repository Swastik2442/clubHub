from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="baseIndex"),
    path("login/", views.login_view, name="loginPage"),
    path("signup/", views.signup_view, name="signupPage"),
    path("logout/", views.logout_view, name="logoutPage"),
    path("dashboard/", views.adminDash, name="adminDash"),
    path("dashboard/add/<int:opt>/", views.adminAdd, name="adminAdd"),
    path("dashboard/edit/<int:opt>/<str:id>/", views.adminEdit, name="adminEdit"),
    path("dashboard/delete/<int:opt>/<str:id>/", views.adminDelete, name="adminDelete"),
    path("dashboard/preview/<int:opt>/", views.adminPreview, name="adminPreview"),
    path("dashboard/executeSQL", views.rawSQL_view, name="adminRawSQL"),
]