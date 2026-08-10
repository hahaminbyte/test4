"""Dashboard analytics for authenticated users."""

from calendar import monthrange
from datetime import UTC, datetime, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from manifest.services.manifest import get_manifests


def get_dashboard_stats(*, username: str) -> dict:
    """Aggregate manifest stats for the user's accessible sites."""
    manifests = get_manifests(username=username).distinct()

    status_label_map = {
        "NotAssigned": ("Not Assigned", "notassigned"),
        "Pending": ("Pending", "pending"),
        "Scheduled": ("Scheduled", "scheduled"),
        "InTransit": ("In Transit", "intransit"),
        "ReadyForSignature": ("Ready Signature", "readyforsignature"),
        "Signed": ("Signed", "signed"),
        "Corrected": ("Corrected", "corrected"),
        "UnderCorrection": ("Under Correction", "undercorrection"),
        "MtnValidationFailed": ("Validation Failed", "mtnvalidationfailed"),
    }
    by_status = []
    for row in manifests.values("status").annotate(value=Count("id")).order_by("status"):
        label, search = status_label_map.get(
            row["status"],
            (row["status"], str(row["status"]).lower()),
        )
        by_status.append({"name": label, "value": row["value"], "searchParam": search})

    now = datetime.now(UTC)
    start = (now.replace(day=1) - timedelta(days=365)).replace(day=1)
    by_month = []
    for row in (
        manifests.filter(created_date__gte=start)
        .annotate(month=TruncMonth("created_date"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    ):
        month = row["month"]
        if month is None:
            continue
        by_month.append(
            {
                "date": month.strftime("%Y-%m"),
                "hazardous": row["total"],
                "nonHazardous": 0,
            }
        )

    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    daily = (
        manifests.filter(created_date__gte=month_start)
        .annotate(day=TruncDate("created_date"))
        .values("day")
        .annotate(haz=Count("id"))
        .order_by("day")
    )
    by_day = {row["day"].day: float(row["haz"] or 0) for row in daily if row.get("day") is not None}
    days_in_month = monthrange(now.year, now.month)[1]
    generator_status = [
        {"day": day, "haz": by_day.get(day, 0.0)} for day in range(1, days_in_month + 1)
    ]

    return {
        "byStatus": by_status,
        "byMonth": by_month,
        "generatorStatus": generator_status,
        "manifestCount": manifests.count(),
    }
