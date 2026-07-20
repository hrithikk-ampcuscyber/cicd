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

### CodeQL (`codeql.yml`) — PRs and pushes to `dev`

GitHub-native SAST; SARIF uploaded to **Security → Code scanning**.

### PR Checks (`pr-checks.yml`) — PRs to `dev`

| Job | Tools | Reports |
|-----|-------|---------|
| dependency-review | GitHub Dependency Review | PR comment summary |
| lint-test | Ruff lint/format, Mypy, Pytest+coverage | JUnit XML, Cobertura XML |
| security-scan | Gitleaks, Semgrep, OSV-Scanner, pip-audit | SARIF + JSON |
| openapi-lint | Spectral | JSON |
| checkov | Checkov (Dockerfile + compose) | SARIF |
| build-scan-sbom | Hadolint, Trivy fs/image, Syft SBOM, pip-licenses | SARIF, JSON, SPDX, CycloneDX, CSV |
| smoke-light | Docker run + health | JSON |
| aggregate-reports | Pipeline summary generator | Consolidated artifact (90-day retention) |

SARIF files are uploaded to **Security → Code scanning alerts**.

### Deploy Test (`deploy-test.yml`) — push to `dev`

Build → Trivy (SARIF+JSON) → SBOM → mock deploy → Schemathesis (JUnit) → OWASP ZAP (HTML+JSON) → E2E (JUnit) → `security-reports-test-<sha>` artifact.

### Deploy Demo (`deploy-demo.yml`) — push to `release/**`

Same as test plus Checkov SARIF. Artifact: `security-reports-demo-<sha>`.

### Deploy Prod (`deploy-prod.yml`) — push to `main`

Checkov SARIF → Trivy CRITICAL (SARIF+JSON) → SBOM verify → mock deploy → smoke only (no ZAP) → `security-reports-prod-<sha>` artifact.

## Report artifacts (IT standard)

Each pipeline run produces a **`security-reports-<sha>`** artifact containing:

| File | Format | Purpose |
|------|--------|---------|
| `*.sarif` | SARIF 2.1 | SAST, SCA, secrets, container, IaC (also in Security tab) |
| `junit-*.xml` | JUnit | Test results in GitHub Checks |
| `coverage.xml` | Cobertura | Code coverage |
| `sbom.spdx.json` | SPDX | Software Bill of Materials |
| `sbom.cyclonedx.json` | CycloneDX | Alternative SBOM format |
| `trivy-*.json` | JSON | Vulnerability scan archive |
| `licenses.csv/json/md` | Multi | License compliance |
| `zap-report.html/json` | HTML/JSON | DAST results (test/demo only) |
| `pipeline-summary.json` | JSON | Consolidated audit manifest |
| `deploy-*.json` | JSON | Mock deployment record |

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

Each deploy workflow uploads a **`security-reports-<env>-<sha>`** bundle (see table above). The deploy manifest JSON is included as `deploy-<env>.json`.
