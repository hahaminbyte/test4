"""Service layer for Org and Site models."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import QuerySet
from guardian.shortcuts import assign_perm
from manifest.services import TaskResponse
from manifest.tasks import sync_site_manifests_task
from org.models import Org, Site

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class SiteServiceError(Exception):
    """Custom exception for Site service errors."""

    def __init__(self, message: str):
        super().__init__(message)


def get_org_by_id(org_id: str) -> Org:
    """Returns an Organization instance or raise a 404."""
    return Org.objects.get(id=org_id)


def get_org_by_slug(org_slug: str) -> Org:
    """Returns an Organization instance or raise a 404."""
    return Org.objects.get_by_slug(org_slug)


@transaction.atomic
def create_org(*, name: str, admin: "User") -> Org:
    """Create an organization and grant the admin view/change access."""
    from profile.services import get_or_create_rcra_profile

    cleaned = name.strip()
    if Org.objects.filter(name__iexact=cleaned).exists():
        msg = "An organization with that name already exists."
        raise ValueError(msg)
    org = Org.objects.create(name=cleaned, admin=admin)
    assign_perm("view_org", admin, org)
    assign_perm("change_org", admin, org)
    # Ensure the admin has a RCRAInfo profile shell for API credentials
    get_or_create_rcra_profile(username=admin.username)
    return org


def _unique_local_epa_id() -> str:
    """Generate a unique 12-character EPA ID for local sample sites."""
    import uuid

    from rcrasite.models import RcraSite

    for _ in range(25):
        # LOC + 9 hex chars = 12 (RCRAInfo site id length)
        candidate = f"LOC{uuid.uuid4().hex[:9].upper()}"
        if not RcraSite.objects.filter(epa_id=candidate).exists():
            return candidate
    msg = "Could not allocate a unique sample EPA ID."
    raise SiteServiceError(msg)


@transaction.atomic
def create_sample_site(*, user: "User", org: Org) -> Site:
    """Create a local demo generator site for an org (no RCRAInfo credentials required)."""
    from profile.models import RcrainfoSiteAccess
    from profile.services import get_or_create_rcra_profile
    from rcrasite.models import Address, Contact, RcraPhone, RcraSite
    from rcrasite.services import ensure_local_demo_handlers

    if not user.has_perm("org.change_org", org) and org.admin_id != user.id:
        msg = "You do not have permission to add sites to this organization."
        raise PermissionError(msg)

    # Ensure mock transporters/TSDF exist for local manifest drafting
    ensure_local_demo_handlers()

    epa_id = _unique_local_epa_id()
    address = Address.objects.create(
        street_number="100",
        address1="Sample Generator Way",
        city="Arlington",
        state="VA",
        country="US",
        zip="22201",
    )
    mail_address = Address.objects.create(
        street_number="100",
        address1="Sample Generator Way",
        city="Arlington",
        state="VA",
        country="US",
        zip="22201",
    )
    phone = RcraPhone.objects.create(number="202-555-0100")
    contact = Contact.objects.create(
        first_name=user.first_name or "Site",
        last_name=user.last_name or "Contact",
        email=user.email or f"{user.username}@localhost",
        phone=phone,
    )
    rcra_site = RcraSite.objects.create(
        epa_id=epa_id,
        name=f"{org.name} Sample Generator",
        site_type="Generator",
        site_address=address,
        mail_address=mail_address,
        contact=contact,
        registered=True,
        can_esign=True,
        limited_esign=False,
        registered_emanifest_user=True,
    )
    site = Site.objects.create(
        name=f"{org.name} Sample Site",
        rcra_site=rcra_site,
        org=org,
    )
    assign_perm("view_site", user, site)
    assign_perm("change_site", user, site)

    rcra_profile, _ = get_or_create_rcra_profile(username=user.username)
    RcrainfoSiteAccess.objects.update_or_create(
        profile=rcra_profile,
        site=epa_id,
        defaults={
            "site_manager": True,
            "annual_report": RcrainfoSiteAccess.CERTIFIER,
            "biennial_report": RcrainfoSiteAccess.CERTIFIER,
            "e_manifest": RcrainfoSiteAccess.CERTIFIER,
            "my_rcra_id": RcrainfoSiteAccess.CERTIFIER,
            "wiets": RcrainfoSiteAccess.CERTIFIER,
        },
    )
    return site


def get_org_rcrainfo_api_credentials(org_id: str) -> tuple[str, str] | None:
    """Returns a tuple of (rcrainfo_api_id, rcrainfo_api_key)."""
    try:
        org = get_org_by_id(org_id)
        if org.is_rcrainfo_integrated:
            return org.rcrainfo_api_id_key
    except Org.DoesNotExist:
        return None


def get_rcrainfo_api_credentials_by_user(user_id: str) -> tuple[str, str] | None:
    """Returns a tuple of (rcrainfo_api_id, rcrainfo_api_key) corresponding to the user's org."""
    try:
        org = Org.objects.get(user_id=user_id)
        if org.is_rcrainfo_integrated:
            return org.rcrainfo_api_id_key
    except Org.DoesNotExist:
        return None


@transaction.atomic
def update_emanifest_sync_date(site: Site, last_sync_date: datetime | None = None):
    """Update the last sync date for a site. Defaults to now if no date is provided."""
    if last_sync_date is not None:
        site.last_rcrainfo_manifest_sync = last_sync_date
    else:
        site.last_rcrainfo_manifest_sync = datetime.now(UTC)
    site.save()


def filter_sites_by_org(org_slug: str) -> QuerySet[Site]:
    """Returns a list of Sites associated with an Org."""
    return Site.objects.filter(org__slug=org_slug).select_related("rcra_site")


def get_user_site(username: str, epa_id: str) -> Site:
    """Returns a user Site if it exists, else throws a DoesNotExist exception."""
    return Site.objects.get_by_username_and_epa_id(username, epa_id)


def get_site_by_epa_id(epa_id: str) -> Site:
    """Returns a Site by its RCRA EPA ID number, else throws a DoesNotExist exception."""
    return Site.objects.get_by_epa_id(epa_id)


def find_sites_by_user(user: "User") -> QuerySet[Site]:
    """Returns a list of Sites associated with a user."""
    return Site.objects.filter_by_user(user)


def filter_sites_by_username(username: str) -> QuerySet[Site]:
    """Returns a list of Sites associated with a user."""
    return Site.objects.filter_by_username(username)


def filter_sites_by_username_and_epa_id(username: str, epa_ids: [str]) -> [Site]:
    """Returns a list of Sites associated with a user."""
    sites: QuerySet = Site.objects.filter_by_username(username)
    other_sites = Site.objects.filter_by_epa_id(epa_ids)
    return [site for site in sites if site in other_sites]


def sync_site_manifest_with_rcrainfo(
    *,
    username: str,
    site_id: str | None = None,
) -> TaskResponse:
    """Launch a batch processing task to sync a site's manifests from RCRAInfo."""
    task = sync_site_manifests_task.delay(site_id=site_id, username=username)
    return {"taskId": task.id}
