"""Custom object level permissions for Site and Org models."""

from rest_framework.permissions import DjangoObjectPermissions


class SiteObjectPermissions(DjangoObjectPermissions):
    """Object level permission for Site model."""

    perms_map = {
        **DjangoObjectPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }

    def has_permission(self, request, view):
        """Allow authenticated users; object-level checks happen in has_object_permission."""
        return bool(request.user and request.user.is_authenticated)


class OrgObjectPermissions(DjangoObjectPermissions):
    """Object level permission for Org model."""

    perms_map = {
        **DjangoObjectPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }

    def has_permission(self, request, view):
        """Allow authenticated users; object-level checks happen in has_object_permission."""
        return bool(request.user and request.user.is_authenticated)
