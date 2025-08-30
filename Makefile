openapi:
	FLASK_APP_IMPORT="app:app" python3 generate_openapi.py

smoke-metrics:
	python3 smoke_metrics.py

