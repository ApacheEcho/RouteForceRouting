import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def init_sentry(app):
    dsn = app.config.get('SENTRY_DSN')
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment="production"
        )