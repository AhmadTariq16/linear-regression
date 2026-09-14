# linear-regression

A simple linear regression training/serving service.

## CI/CD

On every push or pull request to `main`, GitHub Actions runs the test suite.
On push to `main`, it additionally builds the Docker image, scans it with
Trivy (failing on HIGH/CRITICAL vulnerabilities), and pushes it to ECR
tagged with the commit SHA. AWS authentication uses OIDC — no static
credentials are stored in this repository.

An equivalent Jenkins pipeline is defined in the `Jenkinsfile`.
