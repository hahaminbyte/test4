"""Serializers for marshalling/unmarshalling data."""

from collections import OrderedDict

from core.models import (
    TrakUser,
)
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django_celery_results.models import TaskResult
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class TrakUserSerializer(ModelSerializer):
    """Model serializer for marshalling/unmarshalling a user's HaztrakUser."""

    id = serializers.CharField(source="pk")
    username = serializers.CharField(
        required=False,
    )
    firstName = serializers.CharField(
        source="first_name",
        required=False,
    )
    lastName = serializers.CharField(
        source="last_name",
        required=False,
    )

    walletAddress = serializers.CharField(
        source="wallet_address",
        required=False,
        allow_null=True,
        read_only=True,
    )

    class Meta:
        """Metaclass."""

        model = TrakUser
        fields = [
            "id",
            "username",
            "firstName",
            "lastName",
            "email",
            "walletAddress",
        ]


class LoginSerializer(serializers.Serializer):
    """Validate login credentials."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Authenticate the user."""
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            msg = "Invalid username or password."
            raise serializers.ValidationError(msg)
        if not user.is_active:
            msg = "This account is inactive."
            raise serializers.ValidationError(msg)
        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    """Validate new user registration."""

    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    firstName = serializers.CharField(required=False, allow_blank=True, default="")
    lastName = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_username(self, value):
        """Ensure username is unique."""
        if TrakUser.objects.filter(username__iexact=value).exists():
            msg = "A user with that username already exists."
            raise serializers.ValidationError(msg)
        return value

    def validate_email(self, value):
        """Ensure email is unique."""
        if TrakUser.objects.filter(email__iexact=value).exists():
            msg = "A user with that email already exists."
            raise serializers.ValidationError(msg)
        return value

    def validate_password(self, value):
        """Run Django password validators."""
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def create(self, validated_data):
        """Create user and profile."""
        from profile.services import get_or_create_profile

        user = TrakUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("firstName", ""),
            last_name=validated_data.get("lastName", ""),
        )
        get_or_create_profile(username=user.username)
        return user


class WalletNonceSerializer(serializers.Serializer):
    """Request a wallet sign-in challenge."""

    address = serializers.CharField(required=True, max_length=42)


class WalletLoginSerializer(serializers.Serializer):
    """Complete wallet sign-in with a signed challenge."""

    address = serializers.CharField(required=True, max_length=42)
    signature = serializers.CharField(required=True)
    message = serializers.CharField(required=True)


class TaskResultSerializer(serializers.ModelSerializer):
    """Serializer for status or results of long-running celery tasks."""

    taskId = serializers.CharField(
        source="task_id",
        required=True,
    )
    taskName = serializers.CharField(
        source="task_name",
        required=True,
    )
    status = serializers.ChoiceField(
        required=True,
        choices=["PENDING", "STARTED", "SUCCESS", "FAILURE", "NOT FOUND"],
    )
    createdDate = serializers.DateTimeField(
        source="date_created",
        required=False,
    )
    doneDate = serializers.DateTimeField(
        source="date_done",
        required=False,
    )
    result = serializers.JSONField(
        required=True,
    )

    class Meta:
        """Metaclass."""

        model = TaskResult
        fields = [
            "taskId",
            "taskName",
            "status",
            "createdDate",
            "doneDate",
        ]


class TaskStatusSerializer(serializers.Serializer):
    """Serializer for status or results of long-running celery tasks."""

    taskId = serializers.CharField(
        source="task_id",
        required=True,
    )
    taskName = serializers.CharField(
        source="task_name",
        required=True,
    )
    status = serializers.ChoiceField(
        required=True,
        choices=["PENDING", "STARTED", "SUCCESS", "FAILURE", "NOT FOUND"],
    )
    createdDate = serializers.DateTimeField(
        source="date_created",
        required=False,
    )
    doneDate = serializers.DateTimeField(
        source="date_done",
        required=False,
    )
    result = serializers.JSONField(
        required=False,
        allow_null=True,
    )

    def to_representation(self, instance):
        """Convert model instance to JSON."""
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])
