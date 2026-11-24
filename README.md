# next-departures-api

A small FastAPI service that returns the next tube and Overground departures at a given TfL stop.

It exists to demonstrate a production-style delivery pipeline: tests, image build, deploy, and automatic rollback on a failed smoke test.

## Stack

- **App:** Python, FastAPI
- **Hosting:** Azure Container Apps (Consumption plan)
- **Registry:** GitHub Container Registry (GHCR)
- **CI/CD:** GitHub Actions
- **Infrastructure:** Terraform, with state in HCP Terraform

## Design decisions

- **Terraform owns the platform; the pipeline owns releases.**
  Terraform manages the environment, the app, ingress and identity, and ignores the image and traffic weights.
  GitHub Actions deploys each image as a new revision, smoke-tests it, and only then shifts traffic.
  So a `terraform apply` never rolls back a release.
- **State lives in HCP Terraform**, separate from the Azure subscription, so it outlives any one subscription.
- **GHCR instead of ACR:** no fixed monthly registry cost.
- **No secrets in CI for tests** *(planned)*: the TfL client is injected as a dependency, and tests run against a saved fixture. The TfL key only exists at runtime.
- **OIDC from GitHub to Azure** *(planned)*: no long-lived client secret stored in GitHub.