"""URLs for the core app."""

from django.urls import include, path

from .views import (
    GetCurrentTrakUserView,
    LoginView,
    LogoutView,
    RegisterView,
    SessionView,
    TaskStatusView,
    UpdateCurrentTrakUserView,
    WalletLoginView,
    WalletNonceView,
)

task_patterns = (
    [
        path("<str:task_id>", TaskStatusView.as_view(), name="status"),
    ],
    "task",
)

app_name = "core"
urlpatterns = [
    path("task/", include(task_patterns)),
    path(
        "auth/",
        include(
            [
                path("register", RegisterView.as_view(), name="register"),
                path("login", LoginView.as_view(), name="login"),
                path("wallet/nonce", WalletNonceView.as_view(), name="wallet_nonce"),
                path("wallet/login", WalletLoginView.as_view(), name="wallet_login"),
                path("logout", LogoutView.as_view(), name="logout"),
                path("session", SessionView.as_view(), name="session"),
            ]
        ),
    ),
    path(
        "user/",
        include(
            [
                path("current-user", GetCurrentTrakUserView.as_view(), name="current_user"),
                path("current-user/update", UpdateCurrentTrakUserView.as_view(), name="update_user"),
            ]
        ),
    ),
]
