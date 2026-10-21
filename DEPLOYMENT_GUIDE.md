# EventEase — AWS Deployment Setup Guide

A follow-along guide to stand up the two AWS servers and turn the **deploy-staging** and **deploy-production** pipeline stages green. Follow it top to bottom.

**Who this is for:** whoever on the team is setting up the AWS side.
**Time:** ~45–60 min the first time.
**You need:** access to the AWS Academy Learner Lab, and admin access to the GitHub repo (`NEEVENEMMANUEL/eventease`).

---

## The plan in one line

Rent two always-on computers from AWS (one "staging" = rehearsal, one "production" = live), put Docker on them, then give GitHub the keys to log in and deploy to them automatically on every push.

---

## Step 1 — Start the Learner Lab & open the AWS Console

1. Log into **awsacademy.instructure.com** → your course → **AWS Academy Learner Lab** → **Learner Lab**.
2. Click **Start Lab**. Wait for the dot next to **AWS** to turn **green** (~1 min).
3. Click **AWS** to open the console in a new tab.
4. Top-right corner must read **N. Virginia (us-east-1)**. If not, switch to it. *(The Lab only allows us-east-1 / us-west-2, and the ready-made SSH key lives in us-east-1.)*

> Don't click **End Lab** when you stop for the day — just close the tab. "End Lab" wipes more than a normal stop.

---

## Step 2 — Launch the Staging server (t3.micro)

In the console, search **EC2** → **Instances** → **Launch instances**.

- **Name:** `eventease-staging`
- **AMI:** Amazon Linux 2023 (the default, free-tier eligible)
- **Instance type:** `t3.micro`
- **Key pair:** choose **vockey** (already exists in the Lab)
- **Network settings → Edit → Security group** — create one allowing:
  - **SSH** — port 22 — source: Anywhere (0.0.0.0/0) *(fine for a student demo)*
  - **HTTP** — port 80 — source: Anywhere (0.0.0.0/0)
- **Storage:** 8–16 GB (default is fine)
- Click **Launch instance**.

---

## Step 3 — Launch the Production server (t3.small)

Repeat Step 2 exactly, but:

- **Name:** `eventease-production`
- **Instance type:** `t3.small`
- **Security group:** pick the **same** one you just made (don't create a second).

You now have two instances running.

---

## Step 4 — Give each server a stable address (Elastic IP)

Learner Lab servers get a **new** public IP every time the Lab restarts. An Elastic IP pins the address so you don't re-edit secrets constantly *within* the Lab's lifetime.

In EC2 → **Elastic IPs** → **Allocate Elastic IP address** → Allocate. Then **Actions → Associate** → pick `eventease-staging`. Repeat for a second Elastic IP → associate with `eventease-production`.

Write both IPs down — these are your `STAGING_HOST` and `PROD_HOST`.

---

## Step 5 — Install Docker on both servers

Do this on **each** server. Connect via EC2 → select the instance → **Connect** → **EC2 Instance Connect** → Connect (opens a terminal in the browser). Then paste:

```bash
sudo dnf update -y
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# Install the docker compose plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Get the project files onto the server
git clone https://github.com/NEEVENEMMANUEL/eventease.git ~/eventease
cd ~/eventease
cp .env.example .env     # edit .env if you want to change the DB password etc.
```

Then **close and reopen** the terminal once (so the `docker` group applies). Test with `docker ps` — no error = good.

Do all of Step 5 on the **production** server too.

---

## Step 6 — Create the GHCR token & the Discord webhook

**GHCR token** (lets the servers pull the Docker image from GitHub's registry):

1. GitHub → your avatar → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**.
2. Scope: tick **`read:packages`**. Set a long expiry. Generate and **copy it** (you only see it once).

**Discord webhook** (where deploy results get posted):

1. In your Discord server → a channel → **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook** → **Copy Webhook URL**.

---

## Step 7 — Add the 6 secrets to GitHub

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**. Add these six (names must match **exactly**):

| Secret name | Value |
|-------------|-------|
| `STAGING_HOST` | the staging Elastic IP (e.g. `54.x.x.x`) |
| `PROD_HOST` | the production Elastic IP |
| `EC2_USER` | `ec2-user` |
| `EC2_SSH_KEY` | the **full contents** of the Lab's SSH key file (`labsuser.pem`) — download it from the Lab's **AWS Details** button, open it in a text editor, paste everything including the `-----BEGIN...` and `-----END...` lines |
| `GHCR_TOKEN` | the personal access token from Step 6 |
| `DISCORD_WEBHOOK` | the Discord webhook URL from Step 6 |

---

## Step 8 — Push and watch it deploy

Make any tiny change (or re-run the latest workflow) to trigger a push to `main`. In the repo's **Actions** tab you should now see all four stages go green:

1. **test** ✅
2. **build-and-push** ✅
3. **deploy-staging** ✅ — deploys to staging, smoke-tests `/health`, runs E2E
4. **deploy-production** ✅ — promotes the same image, health-checks, auto-rollback on failure, Discord ping

Then open `http://<PROD_HOST>` in a browser — the live EventEase app. Check the footer version banner matches the latest build. 🎉 Screenshot everything for the report.

---

## Demo-day routine (important for the Learner Lab)

Because the Lab auto-stops after ~4 hrs:

1. **Start Lab** before the demo.
2. If the Elastic IPs changed (they usually survive a stop/start, but if the Lab fully reset they won't), update `STAGING_HOST` / `PROD_HOST` secrets with the new IPs.
3. On each server, the containers may need a nudge: `cd ~/eventease && docker compose up -d`.
4. Push a trivial commit to show the full pipeline running live end-to-end.

---

## Troubleshooting

- **`missing server host`** in deploy → the `STAGING_HOST`/`PROD_HOST` secret is empty or misnamed.
- **SSH `permission denied`** → `EC2_SSH_KEY` is incomplete (must include the BEGIN/END lines) or `EC2_USER` isn't `ec2-user`.
- **`denied` pulling image** → `GHCR_TOKEN` missing `read:packages`, or expired.
- **Health check fails / rolls back** → SSH into the server and run `docker compose logs app` to see why the container won't start.
- **Can't reach the site in a browser** → security group is missing the port 80 rule, or the container isn't running (`docker ps`).
