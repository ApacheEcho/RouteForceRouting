#!/bin/bash
# Run Postman collection with Newman for automation/CI
COLLECTION="RouteForceRouting.postman_collection.json"
ENV="RouteForceRouting.postman_environment.json"

if ! command -v newman &> /dev/null; then
  echo "Newman is not installed. Installing..."
  npm install -g newman
fi

newman run "$COLLECTION" -e "$ENV" --reporters cli,json --reporter-json-export newman_results.json
