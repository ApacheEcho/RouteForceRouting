import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://<your_public_key>@sentry.io/<your_project_id>",  # 🔁 Replace with your real DSN
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.5,  # 🔁 Adjust this if you want full tracing (1.0 = 100%)
    send_default_pii=True    # Optional: captures IPs, user info if using Flask login context
)
