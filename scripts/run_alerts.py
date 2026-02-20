from __future__ import annotations

import sys

from job_finder.alerts import build_alert_email, run_alerts, send_resend_email
from job_finder.env import ensure_resend_key, get_resend_from
from job_finder.profile import load_profile


def main() -> int:
    profile = load_profile()
    new_files = run_alerts(profile)

    if new_files and profile.alert_email_enabled and profile.alert_email_to:
        resend_key, _ = ensure_resend_key()
        if resend_key:
            html = build_alert_email(new_files)
            send_resend_email(
                resend_key,
                profile.alert_email_to,
                "Job Finder Alerts",
                html,
                from_email=get_resend_from(),
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
