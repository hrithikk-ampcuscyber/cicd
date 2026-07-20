# CI/CD Practice — FastAPI Backend

Practice repository for industry-standard CI/CD with GitHub Actions public runners. All security scans and deploy steps run on `ubuntu-latest`; no tools are installed on servers. Deployments are **mocked** (Docker on the runner + deploy artifact JSON).

## Branch strategy

| Branch | Workflow | Mock environment |
|--------|----------|------------------|
| `main` | Empty (README only). `deploy-prod.yml` runs after merge from `release/*` | **prod** |
| `dev` | `pr-checks.yml` (PRs), `deploy-test.yml` (push) | **test** |
| `release/*` | `deploy-demo.yml` (push) | **demo** |

```text
main (empty)  ←── PR merge ──  release/1.0.0  ←── branch ──  dev
                                      │                         │
                                 demo deploy              test deploy
                                      │
                               cherry-pick bugfixes → dev
```

## Application

FastAPI service with:

- `GET /health` — health check (returns environment + version)
- `POST /api/v1/items` — create item
- `GET /api/v1/items/{id}` — get item
- `GET /api/v1/items` — list items

### Run locally

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
curl http://localhost:8000/health
```

### Run tests

```bash
pytest tests/unit tests/integration -v
# E2E (requires running server):
docker build -t practice-api:local -f infra/docker/Dockerfile .
docker run -d -p 8000:8000 -e ENVIRONMENT=local practice-api:local
BASE_URL=http://localhost:8000 pytest tests/e2e -v -m e2e
```

## CI/CD pipelines

### PR Checks (`pr-checks.yml`) — PRs to `dev`

| Job | Tools |
|-----|-------|
| lint-test | Ruff, Mypy, Pytest |
| security-scan | Gitleaks, Semgrep, OSV-Scanner |
| openapi-lint | Spectral |
| checkov | Checkov (Dockerfile + compose) |
| build-scan-sbom | Docker build, Trivy, Syft SBOM, pip-licenses |
| smoke-light | Docker run + curl `/health` |

### Deploy Test (`deploy-test.yml`) — push to `dev`

Build → Trivy → SBOM → mock deploy → Schemathesis → OWASP ZAP → E2E → promote `test-approved` artifact.

### Deploy Demo (`deploy-demo.yml`) — push to `release/**`

Same as test plus Checkov env scan. Promotes `demo-approved` artifact.

### Deploy Prod (`deploy-prod.yml`) — push to `main`

Checkov → Trivy (CRITICAL only) → SBOM verify → mock deploy → smoke only (no ZAP) → promote `prod` artifact.

## Practice workflow

```bash
# 1. Work on dev (triggers test deploy on push)
git checkout dev
git push origin dev

# 2. Freeze for release
git checkout -b release/1.0.0
git push origin release/1.0.0          # → demo deploy

# 3. Bugfix on release, cherry-pick to dev
git checkout release/1.0.0
# fix, commit, push                     # → demo deploy again
git checkout dev
git cherry-pick <commit-sha>
git push                                # → test deploy

# 4. Promote to prod
gh pr create --base main --head release/1.0.0
# merge PR                              # → prod deploy
```

## GitHub setup (recommended)

Create environments in **Settings → Environments**: `test`, `demo`, `production`. Add required reviewers on `production` to practice approval gates.

## Mock deploy artifacts

Each deploy workflow uploads a JSON file under **Actions → run → Artifacts**, e.g. `deploy-test-<sha>/deploy-test.json`.
