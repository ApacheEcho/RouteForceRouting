# Keploy Automated Testing Workflow for Flask

## 1. Install Keploy CLI

Run this in your terminal:
```sh
curl --silent -O -L https://keploy.io/install.sh && source install.sh
```

## 2. Record API Traffic

### For Local Flask App
```sh
keploy record -c "python3 app.py"
```

### For Docker Compose
```sh
keploy record -c "docker compose up" --container-name "flask-app" --buildDelay 50
```

- While recording, use your app or run API tests (curl/Postman/etc.).
- Keploy will generate test cases and mocks in the `tests` directory.

## 3. Replay Tests

### For Local Flask App
```sh
keploy test -c "python3 app.py" --delay 10
```

### For Docker Compose
```sh
keploy test -c "docker compose up" --container-name "flask-app" --buildDelay 50 --delay 10
```

## 4. Combine Coverage (Optional)

If you want to combine Keploy API test coverage with your unit tests:
```sh
python3 -m coverage combine
python3 -m coverage report
python3 -m coverage html
```

## 5. CI/CD Integration

- Add Keploy record and test steps to your CI pipeline (e.g., GitHub Actions).
- Use the same commands as above in your workflow scripts.

## 6. Tips
- Explore the `tests` and `mocks.yml` files Keploy generates.
- You can edit or replay tests as needed.
- For more, see the [Keploy Flask Quickstart](https://keploy.io/docs/quickstart/samples-flask/).

---

Happy testing with Keploy! 🚀
