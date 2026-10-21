# EventEase — Project Progress

**Unit:** SWE40006 Software Deployment and Evolution — Group CL02_Fri12:30_G06
**Goal:** A containerised web app with a full CI/CD pipeline (push → test → build → deploy to staging → deploy to production), targeting **Level 4** (fully automated push-to-deploy).
**Last updated:** 15 Oct 2026

---

## The pipeline at a glance

Every `git push` to `main` triggers four stages:

| Stage | What it does | Status |
|-------|--------------|--------|
| **1. test** | Lint (flake8) + 38 unit/integration tests + 70% coverage gate, run against a real Postgres | ✅ **Green** |
| **2. build-and-push** | Builds ONE Docker image per commit, tags it with the commit SHA, pushes to GitHub Container Registry (GHCR) | ✅ **Green** |
| **3. deploy-staging** | Pulls that exact image onto the Staging EC2, smoke-tests `/health`, runs Playwright E2E | ⏳ Waiting on AWS servers |
| **4. deploy-production** | Promotes the SAME image to Production, health-checks it, **auto-rolls back** on failure, posts result to Discord | ⏳ Waiting on AWS servers |

So the "build once, deploy many" half is done and proven. The remaining half is standing up the AWS servers and wiring the secrets so stages 3 and 4 light up.

---

## ✅ Done & working

- **The app (EventEase)** — Flask + PostgreSQL. Post events, sign up, capacity + duplicate-email checks, `/health` endpoint, `/metrics` (Prometheus) endpoint, and a footer version banner showing build number + commit SHA (proof of which build is live).
- **Styling (CSS)** — done.
- **Containerisation** — Dockerfile, docker-compose (app + db + nginx), Nginx reverse proxy config.
- **Testing** — 38 tests (unit + integration), 98% coverage, plus a Playwright E2E suite for the live deployment.
- **GitHub repo** — set up, all 3 members added as collaborators, `.github/workflows/ci.yml` pipeline committed.
- **CI (stage 1 + 2)** — lint + test + build + publish to GHCR, all green. The `eventease` package is published and visible on the repo.
- **Monitoring config** — Prometheus scrape config written (`monitoring/prometheus.yml`).

## 🔧 Left to do

1. **AWS EC2 servers** — launch 2 instances in the AWS Academy Learner Lab (Staging `t3.micro` + Production `t3.small`), install Docker. *(in progress)*
2. **GitHub secrets** — add the 6 secrets the deploy jobs need (server IPs, SSH key, GHCR token, Discord webhook).
3. **deploy-staging** → go green.
4. **deploy-production** → go green (incl. auto-rollback + Discord alert).
5. **Monitoring live** — get Grafana + Node Exporter running on the Production server (config exists; the server has to be up first) and screenshot the dashboards.
6. **Presentation** (Week 11) — not started.
7. **Final report** (Week 12) — not started.

---

## Who's doing what (proposed split)

- **Emmanuel** — built the app + pipeline, leading the AWS/EC2 setup. Owns the **deployment pipeline demo** + that section of the report.
- **Thindu** — **monitoring**: get Grafana + Prometheus + Node Exporter dashboards live on prod, screenshot them, write the monitoring section.
- **Raaz** — **testing story** (unit / integration / E2E / coverage) + lead the **presentation slides** and pull the **report** together.

Everyone contributes to the report + presentation (keeps the shared-contribution requirement satisfied).

---

## Evidence to collect for the report

Keep screenshotting as we go — these are the "proof it works" shots the report wants:

- GitHub Actions runs (the green ticks on test + build + deploy).
- The published `eventease` package in GHCR.
- Any build/run errors + how they were fixed (great for the "challenges" section — we already have a few: the test import-path fix and the GHCR lowercase fix).
- The live app running on the EC2 public IP.
- The footer version banner changing between deploys (proof the new build went live).
- The auto-rollback firing (deploy a deliberately broken build, watch it roll back).
- Grafana dashboards showing live metrics.
- The Discord deploy notification.

---

## A note on tooling

The team designed the architecture and made the engineering decisions — what the app does, the tech stack, the pipeline stages, the monitoring approach. AI was used to speed up boilerplate and debugging, the way you'd use any modern dev tool. Everyone on the team understands how the pieces fit together, which is what the demo Q&A will test.
