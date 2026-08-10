"""Views for the org app."""

from http import HTTPStatus

from org.filters import ObjectPermissionsFilter
from org.models import Org, Site
from org.permissions import OrgObjectPermissions, SiteObjectPermissions
from org.serializers import OrgSerializer, SiteSerializer
from org.services import (
    SiteServiceError,
    create_org,
    create_sample_site,
    filter_sites_by_org,
    find_sites_by_user,
    get_org_by_slug,
    get_site_by_epa_id,
)
from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class CreateOrgSerializer(serializers.Serializer):
    """Validate organization creation."""

    name = serializers.CharField(max_length=200, min_length=2)


class OrgCreateView(APIView):
    """Create a new organization owned by the current user."""

    def post(self, request: Request) -> Response:
        """Create org."""
        serializer = CreateOrgSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            org = create_org(name=serializer.validated_data["name"], admin=request.user)
        except ValueError as exc:
            return Response({"name": [str(exc)]}, status=HTTPStatus.BAD_REQUEST)
        return Response(OrgSerializer(org).data, status=HTTPStatus.CREATED)


class OrgDetailsView(RetrieveAPIView):
    """Retrieve details for a given Org."""

    serializer_class = OrgSerializer
    queryset = Org.objects.all()
    lookup_url_kwarg = "org_slug"
    permission_classes = [OrgObjectPermissions]

    def get_object(self):
        """Get organization."""
        org = get_org_by_slug(self.kwargs["org_slug"])
        self.check_object_permissions(self.request, org)
        return org


class OrgListView(ListAPIView):
    """that returns all haztrak organization that the user has access to."""

    serializer_class = OrgSerializer
    queryset = Org.objects.all()
    filter_backends = [ObjectPermissionsFilter]


class SiteListView(ListAPIView):
    """that returns all haztrak sites that the user has access to."""

    serializer_class = SiteSerializer
    queryset = Site.objects.all()
    filter_backends = [ObjectPermissionsFilter]

    def get_queryset(self):
        """Get org sites."""
        if "org_slug" in self.kwargs:
            return filter_sites_by_org(self.kwargs["org_slug"])
        return find_sites_by_user(self.request.user)


class SampleSiteCreateView(APIView):
    """Create a local sample site for an organization (no EPA credentials required)."""

    def post(self, request: Request, org_slug: str) -> Response:
        """Create sample site."""
        org = get_org_by_slug(org_slug)
        if not request.user.has_perm("org.view_org", org):
            return Response(
                {"detail": "You do not have access to this organization."},
                status=HTTPStatus.FORBIDDEN,
            )
        try:
            site = create_sample_site(user=request.user, org=org)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=HTTPStatus.FORBIDDEN)
        except SiteServiceError as exc:
            return Response({"detail": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        return Response(SiteSerializer(site).data, status=HTTPStatus.CREATED)


class SiteDetailsView(RetrieveAPIView):
    """View details of a Haztrak Site."""

    serializer_class = SiteSerializer
    lookup_url_kwarg = "epa_id"
    queryset = Site.objects.all()
    permission_classes = [SiteObjectPermissions]

    def get_object(self):
        """Get the object."""
        site = get_site_by_epa_id(epa_id=self.kwargs["epa_id"])
        self.check_object_permissions(self.request, site)
        return site
