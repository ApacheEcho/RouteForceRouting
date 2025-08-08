# Decision Record: Remove Kubernetes Artifacts

Date: 2025-08-08
Status: Accepted

## Context
Kubernetes manifests and workflows existed in the repository but were not actively used for deployment. The project now standardizes on Render for deployment. Retaining unused K8s code and CI jobs increases maintenance and security surface.

## Decision
- Remove `k8s/` directory and all Kubernetes manifests.
- Remove Kubernetes deployment jobs and references from CI workflows.
- Deprecate `deploy-cloud.sh` script.

## Consequences
- Reduced complexity and attack surface.
- CI/CD simplified to testing, security scanning, and Docker image publishing.
- If Kubernetes is needed in the future, add back manifests in a dedicated branch or via a new ADR.

## Related
- `.github/workflows/ci-cd.yml` updated
- `deploy-cloud.sh` deprecated
