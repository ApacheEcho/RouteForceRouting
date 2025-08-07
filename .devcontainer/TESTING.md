# 🧪 Testing Your GitHub Codespaces Setup

## Quick Validation Checklist

After your Codespace loads, run these commands to verify everything is working:

### 1. Check Python Environment
```bash
python --version          # Should show Python 3.12.x
which python             # Should show /usr/local/bin/python
pip list | grep -E "(flask|pytest|redis|psycopg2)"
```

### 2. Verify Services
```bash
# Check PostgreSQL
pg_isready -h postgres -p 5432 -U routeforce
# Expected: postgres:5432 - accepting connections

# Check Redis  
redis-cli -h redis ping
# Expected: PONG

# List running containers
docker ps
# Should show postgres, redis, and pgadmin containers
```

### 3. Test Database Connection
```bash
# Connect to PostgreSQL
psql -h postgres -U routeforce -d routeforce_dev
# Password: password
# Should connect successfully

# In psql prompt:
\l                       # List databases
\q                       # Quit
```

### 4. Run Development Commands
```bash
# Test aliases
rf-deps                  # Install dependencies
rf-test                  # Run tests (may fail initially - that's OK)
rf-lint                  # Check code quality
```

### 5. Start the Application
```bash
rf-run                   # Start Flask server
# Should start on http://localhost:5000
# VS Code will show port forwarding notification
```

### 6. Test Port Forwarding
- **Flask App**: http://localhost:5000
- **PgAdmin**: http://localhost:8080 (admin@routeforce.local / admin)

### 7. Check VS Code Extensions
Open Command Palette (`Cmd/Ctrl + Shift + P`) and verify these extensions are installed:
- Python
- Black Formatter  
- Flake8
- GitHub Copilot
- Docker
- GitLens

## 🚨 Troubleshooting

### Services Not Starting
```bash
# Check service status
docker-compose ps

# Restart services
cd .devcontainer
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs postgres
docker-compose logs redis
```

### Python Dependencies Issues
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Database Connection Problems
```bash
# Wait for services to fully start
sleep 10

# Test connection manually
PGPASSWORD=password psql -h postgres -U routeforce -d routeforce_dev -c "SELECT version();"
```

### Port Forwarding Issues
1. Check the **PORTS** tab in VS Code terminal panel
2. Look for ports 5000, 5432, 6379, 8080
3. Click the "Open in Browser" icon next to port 5000

## ✅ Success Indicators

You know everything is working when:
- ✅ Python 3.12 is available
- ✅ PostgreSQL accepts connections
- ✅ Redis responds to ping
- ✅ Flask app starts without errors
- ✅ PgAdmin loads at port 8080
- ✅ All VS Code extensions are active
- ✅ Development aliases work (`rf-run`, `rf-test`, etc.)

## 🎯 Next Steps

Once validated:
1. **Configure API keys** in `.env` file
2. **Run database migrations**: `rf-db-upgrade`  
3. **Start development**: `rf-run`
4. **Open your app**: VS Code will forward the port automatically

## 📝 Reporting Issues

If something isn't working:
1. **Check the terminal output** for error messages
2. **Run the validation commands** above
3. **Check service logs**: `docker-compose logs [service-name]`
4. **Create an issue** with the error details and steps to reproduce

---

**🎉 Ready to code!** Your RouteForceRouting development environment should now be fully operational.
