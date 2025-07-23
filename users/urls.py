from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("logout/", views.user_logout, name="logout"),
    path("manage/users/", views.user_list, name="user_list"),
    path(
        "manage/users/<int:user_id>/permissions/",
        views.user_permissions,
        name="user_permissions",
    ),
    path("manage/users/add/", views.add_user, name="add_user"),
    path("manage/users/<int:user_id>/delete/", views.delete_user, name="delete_user"),
    path(
        "manage/users/<int:user_id>/reset-password/",
        views.reset_user_password,
        name="reset_user_password",
    ),
    path("profile/", views.user_profile, name="profile"),
    path("profile/change-password/", views.change_password, name="change_password"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
