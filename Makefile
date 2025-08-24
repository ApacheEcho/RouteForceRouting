# Makefile for RouteForceRouting

.PHONY: openapi

openapi:
	FLASK_APP_IMPORT="app:app" python3 generate_openapi.py

# Add more targets as needed
