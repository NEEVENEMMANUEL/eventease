# EventEase Monitoring (Prometheus + Grafana + Node Exporter)

Live "vital signs" for the production server and the EventEase app. This stack
runs **on the Production EC2 server**, alongside the app.

## What's in here

| File | What it does |
|------|--------------|
| `docker-compose.yml` | Runs Prometheus, Grafana and Node Exporter as containers |
| `prometheus.yml` | Tells Prometheus what to scrape (the app's `/metrics` + node-exporter) |
| `grafana/provisioning/…` | Auto-adds the Prometheus data source **and** the dashboard, so Grafana is ready with zero clicking |

**The three pieces:** Node Exporter exposes the server's CPU/RAM/disk vitals · Prometheus scrapes & stores them (plus the app's request metrics) · Grafana draws them as live graphs.

---

## How to run it (on the Production server)

**1. Open the Grafana port in the security group.** In the AWS console → EC2 →
your instance's **Security group** → **Edit inbound rules** → add:
`Custom TCP · port 3000 · source Anywhere (0.0.0.0/0)` → Save. *(This is how you'll reach Grafana in a browser.)*

**2. Connect to the Production server** (EC2 → `eventease-production` → Connect → EC2 Instance Connect), then:

```bash
cd ~/eventease
git pull                                        # get these monitoring files
docker compose -f monitoring/docker-compose.yml up -d
```

**3. Wait ~30 seconds**, then in a browser open:

```
http://<PRODUCTION_PUBLIC_IP>:3000
```

Log in with **admin / admin** (it'll ask you to set a new password — any value is fine).

**4. You're done.** Click **Dashboards** (left menu) → **EventEase — Production Overview**. The Prometheus data source and this dashboard are already loaded — no setup needed. You'll see CPU, memory, and the app's request rate / latency / status codes updating live.

**5. Make the app graphs move:** open the live app a few times (refresh `http://<PRODUCTION_PUBLIC_IP>/`, post an event, sign up) — that traffic shows up on the "App Request Rate" and "HTTP Requests by Status" panels within ~15s.

**6. Screenshot the dashboard** for the report. That's your "we can observe production" proof. 📸

---

## Optional: the famous full server dashboard

Grafana → **Dashboards** → **New** → **Import** → enter ID **`1860`** → select the **Prometheus** data source → **Import**. That's the community "Node Exporter Full" dashboard — dozens of detailed server panels. Nice extra screenshot for the report.

---

## Troubleshooting

- **Grafana page won't load** → the port 3000 inbound rule (step 1) isn't added, or the containers aren't up yet (`docker compose -f monitoring/docker-compose.yml ps`).
- **App panels say "No data"** (but CPU/memory work) → Prometheus can't reach the app. Check the app network name with `docker network ls` — it should be `eventease_default`. If it's different, edit the `name:` under the `eventease` network in `monitoring/docker-compose.yml` to match, then `docker compose -f monitoring/docker-compose.yml up -d` again.
- **Check what Prometheus sees** → open `http://<PRODUCTION_PUBLIC_IP>:9090/targets` (needs port 9090 opened too) — both `eventease-app` and `node-exporter` targets should show **UP**.

---

## Stopping it

```bash
docker compose -f monitoring/docker-compose.yml down
```

(Add `-v` to also wipe the stored metrics/dashboards — usually you don't want that.)
