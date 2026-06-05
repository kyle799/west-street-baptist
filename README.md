# West Street Baptist Church — Website

A simple public website for West Street Baptist Church (Pueblo, CO): Django + Postgres
behind nginx, containerized with blue/green deploys, plus an embedded Bible reader.

- **Stack:** Django (gunicorn) · PostgreSQL · nginx · Flask Bible reader (`bible_flask_api`)
- **Pages:** Home, About/Beliefs, Visit, Contact, Prayer Request, Bible reader at `/bible`
- **Forms:** Contact + Prayer submissions persist to Postgres and are reviewed in Django admin
- **Brand:** [`BRAND.md`](./BRAND.md) ← `west-street-baptist-brand-sheet.html` (source of truth)

> `online-sermon/` is a **reference-only** sibling project (not deployed); its proven
> blue/green, nginx, and CI patterns and its contact/prayer data model are reused here.

## Local development

```bash
cp .env.example .env            # optional for dev; compose has dev defaults
docker compose up -d postgres web bible

# One-time: load Bible translations
git clone https://github.com/seven1m/open-bibles bibles
docker compose run --rm importer --bibles-dir /bibles --only eng-web,eng-kjv,eng-asv

# Create an admin user to review submissions
docker compose exec web python manage.py createsuperuser
```

- Site: http://localhost:8000  · Admin: http://localhost:8000/admin
- Bible reader (direct): http://localhost:5002/bible — behind nginx it lives at `/bible`
- Full nginx routing locally: `docker compose --profile proxy up -d nginx` → http://localhost:8080

## Production (blue/green)

`docker-compose.prod.yml` defines `web-blue` + `web-green`; only one serves at a time.
`scripts/deploy-swap.sh` starts the idle color, waits for its `/healthz` healthcheck,
repoints `nginx/active-upstream.conf`, graceful-reloads nginx, and drains the old color.

GitHub CI:
- **`ci.yml`** (PRs): Django check, `makemigrations --check`, tests, image builds.
- **`deploy.yml`** (push to `main`): build & push `web`/`bible` images to GHCR, then run
  `deploy-swap.sh` on the self-hosted VPS runner.

### Migration discipline
Both colors share one database and overlap briefly during a swap, so schema changes must
be **expand-only** (add columns/tables/indexes). Drops/renames need a two-deploy dance:
first stop using the old shape, then remove it in a later deploy.

## TLS

Default nginx profile is `conf.d.cloudflare` (plain HTTP behind a Cloudflare tunnel).
Set `NGINX_PROFILE` to switch profiles.
# west-street-baptist
