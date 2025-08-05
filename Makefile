# RouteForce Documentation Makefile
# Provides convenient commands for documentation generation and management

.PHONY: help docs docs-install docs-test docs-serve docs-clean docs-validate

# Default target
help:
	@echo "RouteForce API Documentation Commands:"
	@echo ""
	@echo "  docs-install    Install documentation dependencies"
	@echo "  docs-test       Test documentation setup"
	@echo "  docs            Generate API documentation"
	@echo "  docs-serve      Serve documentation locally (port 8080)"
	@echo "  docs-validate   Validate OpenAPI specification"
	@echo "  docs-clean      Clean generated documentation"
	@echo ""

# Install documentation dependencies
docs-install:
	@echo "📦 Installing documentation dependencies..."
	pip install flask-restx flask-caching flask-cors flask-limiter flask-socketio
	pip install flask-sqlalchemy flask-migrate
	pip install psutil
	@echo "✅ Documentation dependencies installed"

# Test documentation setup
docs-test:
	@echo "🧪 Testing API documentation setup..."
	python test_api_docs.py

# Generate API documentation
docs:
	@echo "📚 Generating API documentation..."
	python scripts/generate_docs.py
	@echo "✅ Documentation generated in docs/api/"

# Serve documentation locally
docs-serve:
	@echo "🌐 Serving documentation at http://localhost:8080"
	@echo "Press Ctrl+C to stop the server"
	cd docs/api && python -m http.server 8080

# Validate OpenAPI specification
docs-validate:
	@echo "🔍 Validating OpenAPI specification..."
	@if [ -f docs/api/openapi.json ]; then \
		python -m json.tool docs/api/openapi.json > /dev/null && echo "✅ OpenAPI JSON is valid"; \
	else \
		echo "❌ OpenAPI specification not found. Run 'make docs' first."; \
	fi

# Clean generated documentation
docs-clean:
	@echo "🧹 Cleaning generated documentation..."
	rm -rf docs/api/
	@echo "✅ Documentation cleaned"

# Quick setup for new developers
docs-setup: docs-install docs-test docs
	@echo ""
	@echo "🎉 Documentation setup complete!"
	@echo "✅ Dependencies installed"
	@echo "✅ System tested"
	@echo "✅ Documentation generated"
	@echo ""
	@echo "Next steps:"
	@echo "  - Run 'make docs-serve' to view documentation locally"
	@echo "  - Check docs/API_DOCUMENTATION_GUIDE.md for contributor guide"
	@echo "  - Visit http://localhost:8000/api/docs/ when running the app"