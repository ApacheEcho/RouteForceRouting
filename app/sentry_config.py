import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def init_sentry():
    sentry_sdk.init(
        dsn="https://your-dsn@o123456.ingest.sentry.io/1234567",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

def register_test_routes(app):
    @app.route("/sentry-test")
    def trigger_error():
        division_by_zero = 1 / 0
        return str(division_by_zero)