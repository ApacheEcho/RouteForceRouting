# RouteForceRouting API Automation

This repo includes a ready-to-use Postman collection and environment for automated API testing.

## How to Use in VS Code

1. **Open the Postman extension sidebar.**
2. **Import** `RouteForceRouting.postman_collection.json` and `RouteForceRouting.postman_environment.json`.
3. **Set the environment** to `RouteForceRouting Local`.
4. **Run requests or the whole collection** using the extension's Runner.
5. **View test results** in the extension.

## How to Run Automation from CLI/CI

1. Make sure you have [Node.js](https://nodejs.org/) and [Newman](https://www.npmjs.com/package/newman) installed.
2. Run:

```sh
bash run_postman_automation.sh
```

- This will run all API tests and output results to `newman_results.json`.

## Customization

- Edit the collection to add more endpoints or tests.
- Update the environment file for different base URLs or tokens.

## References

- [Postman VS Code Extension Docs](https://learning.postman.com/docs/developer/vs-code-extension/overview/)
- [Newman CLI Docs](https://www.npmjs.com/package/newman)
