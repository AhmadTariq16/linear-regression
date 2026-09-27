# linear-regression with a twist of Ops

A simple linear regression service built to practise the Ops around it. A scikit-learn
model is trained on sample data and served through a FastAPI endpoint. A CI pipeline
(GitHub Actions, with an equivalent Jenkinsfile) runs the tests, builds a Docker image,
scans it with Trivy and pushes it to Amazon ECR. The AWS resources, including OIDC
authentication for CI, are managed with Terraform.
