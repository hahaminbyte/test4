"""Views for the core app."""

from http import HTTPStatus

from core.serializers import (
    LoginSerializer,
    RegisterSerializer,
    TrakUserSerializer,
    WalletLoginSerializer,
    WalletNonceSerializer,
)
from core.services import get_task_status
from core.services.wallet_auth import (
    WalletAuthError,
    get_or_create_wallet_user,
    issue_wallet_nonce,
    verify_wallet_signature,
)
from django.conf import settings
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django_celery_results.models import TaskResult
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class TaskStatusView(APIView):
    """retrieve the status of long-running tasks."""

    queryset = TaskResult.objects.all()

    def get(self, request: Request, task_id):
        """Retrieve the status of a task."""
        try:
            data = get_task_status(task_id)
            return Response(data=data, status=HTTPStatus.OK)
        except KeyError:
            return Response(
                data={"error": "malformed request"},
                status=HTTPStatus.BAD_REQUEST,
            )
        except ValidationError:
            return Response(
                data={"error": "problem validating request"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except TaskResult.DoesNotExist:
            return Response(data={"taskId": "unknown"}, status=HTTPStatus.OK)


class GetCurrentTrakUserView(RetrieveAPIView):
    """Get the current user."""

    serializer_class = TrakUserSerializer

    def get_object(self):
        """Get the current user."""
        return self.request.user


class UpdateCurrentTrakUserView(UpdateAPIView):
    """Update the current authenticated user."""

    serializer_class = TrakUserSerializer

    def get_object(self):
        """Get the current user."""
        return self.request.user


class RegisterView(APIView):
    """Create a new user account and log them in."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request: Request) -> Response:
        """Register a new user."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
        return Response(
            {
                "user": TrakUserSerializer(user).data,
            },
            status=HTTPStatus.CREATED,
        )


class LoginView(APIView):
    """Authenticate with username and password."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request: Request) -> Response:
        """Log in."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
        return Response(
            {
                "user": TrakUserSerializer(user).data,
            },
            status=HTTPStatus.OK,
        )


class LogoutView(APIView):
    """End the current session."""

    def post(self, request: Request) -> Response:
        """Log out."""
        logout(request)
        return Response(status=HTTPStatus.NO_CONTENT)


class WalletNonceView(APIView):
    """Issue a one-time message for wallet personal_sign."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request: Request) -> Response:
        """Create nonce challenge."""
        serializer = WalletNonceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            challenge = issue_wallet_nonce(serializer.validated_data["address"])
        except WalletAuthError as exc:
            return Response({"detail": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        return Response(challenge, status=HTTPStatus.OK)


class WalletLoginView(APIView):
    """Verify wallet signature and create a session (sign-in or sign-up)."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request: Request) -> Response:
        """Verify signature and log in."""
        serializer = WalletLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            address = verify_wallet_signature(
                address=serializer.validated_data["address"],
                signature=serializer.validated_data["signature"],
                message=serializer.validated_data["message"],
            )
            user, created = get_or_create_wallet_user(address)
        except WalletAuthError as exc:
            return Response({"detail": str(exc)}, status=HTTPStatus.BAD_REQUEST)

        if not user.is_active:
            return Response(
                {"detail": "This account is inactive."},
                status=HTTPStatus.FORBIDDEN,
            )

        login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
        return Response(
            {
                "user": TrakUserSerializer(user).data,
                "created": created,
            },
            status=HTTPStatus.CREATED if created else HTTPStatus.OK,
        )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SessionView(APIView):
    """Return the current session user, if any."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]

    def get(self, request: Request) -> Response:
        """Get session."""
        if request.user.is_authenticated:
            return Response(
                {
                    "isAuthenticated": True,
                    "user": TrakUserSerializer(request.user).data,
                },
            )
        return Response({"isAuthenticated": False, "user": None})
