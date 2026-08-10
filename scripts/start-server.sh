#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_DIR="$ROOT_DIR/server"

cd "$SERVER_DIR"

if command -v uv >/dev/null 2>&1; then
  uv sync --dev >/dev/null
  PY=(uv run python)
else
  PY=(python3)
fi

"${PY[@]}" manage.py migrate --noinput

# Ensure local mock transporters/TSDF exist for drafting manifests without EPA credentials.
"${PY[@]}" manage.py shell <<'PY'
from rcrasite.services import ensure_local_demo_handlers
created = ensure_local_demo_handlers()
if created:
    print(f"Created local demo handlers: {', '.join(s.epa_id for s in created)}")
PY

USER_COUNT="$("${PY[@]}" manage.py shell -c 'from core.models import TrakUser; print(TrakUser.objects.count())' 2>/dev/null | tail -1)"
if [[ "${USER_COUNT:-0}" == "0" ]]; then
  echo "Seeding development data..."
  "${PY[@]}" manage.py loaddata core/fixtures/core_dev.yaml \
    rcrasite/fixtures/rcrasite_dev.yaml \
    org/fixtures/org_dev.yaml \
    profile/fixtures/profile_dev.yaml
fi

# Ensure seed accounts have a usable local password (idempotent).
"${PY[@]}" manage.py shell <<'PY'
from core.models import TrakUser
for username in ("admin", "testuser1", "orgadmin"):
    user = TrakUser.objects.filter(username=username).first()
    if user is None:
        continue
    if not user.has_usable_password() or not user.check_password("password1"):
        user.set_password("password1")
        user.save()
        print(f"Set password for {username}")
PY

exec "${PY[@]}" manage.py runserver 127.0.0.1:8000
