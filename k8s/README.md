# Kubernetes Manifests (Optional)

These manifests are provided as optional references and are not used by the current CI/CD pipeline.

- Primary deployment target is Render.com.
- CI jobs referencing Kubernetes are disabled.
- Secrets and cluster context are intentionally not wired for security.

If you plan to use Kubernetes:
- Create appropriate namespaces and secrets.
- Replace image references and environment variables to match your infra.
- Re-enable or add a dedicated deployment workflow.

If Kubernetes is not required for your deployment, you can ignore this folder.
