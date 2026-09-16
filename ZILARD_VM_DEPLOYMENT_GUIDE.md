# ZILARD Website + DLDMS — VM Deployment Guide

Target: Ubuntu/Debian virtual machine on imbra, serving the Django project via **Gunicorn + Nginx + systemd**, backed by **PostgreSQL**, with the public ZILARD website at `/` and the internal DLDMS system at `/app/`.

Work through the sections in order. Each step assumes you're SSH'd into the VM unless noted otherwise.

---

## 0. Before you start

Gather these first:

- SSH access to the imbra VM (IP address or hostname, a non-root user with `sudo`)
- A domain name pointed at the VM's IP (an A record), if you want HTTPS with a real certificate — otherwise you can deploy on the bare IP first and add the domain later
- The project folder from your Windows machine: `C:\Users\Director\Documents\Codex\2026-06-30\you-are-an-expert-full-stack`
- A way to transfer files to the VM (SCP/SFTP client such as WinSCP, or Git if the project is in a repository)

Decide on:

- **Domain or IP** you'll use to reach the site (example used below: `zilard.co.zm` — replace throughout)
- **Database name/user/password** for PostgreSQL
- A **new `SECRET_KEY`** for production (never reuse the one in your local `.env`/settings)

---

## 1. Provision the VM

On imbra, create/confirm a VM with:

- Ubuntu 22.04 LTS or 24.04 LTS
- At least 1 vCPU / 2 GB RAM / 20 GB disk (comfortable for this site; bump RAM if the internal DLDMS system sees heavy concurrent use)
- A public/static IP, with port 22 (SSH) reachable from your admin IP

SSH in and update the system:

```bash
ssh youruser@YOUR_VM_IP
sudo apt update && sudo apt upgrade -y
```

Create a dedicated non-root deploy user if you're currently root:

```bash
sudo adduser zilard
sudo usermod -aG sudo zilard
su - zilard
```

---

## 2. Install system packages

```bash
sudo apt install -y python3 python3-venv python3-pip python3-dev \
    build-essential libpq-dev \
    postgresql postgresql-contrib \
    nginx \
    git \
    ufw
```

---

## 3. Set up the firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

This opens SSH (22), HTTP (80), and HTTPS (443) only. Gunicorn will listen on a local socket/port that Nginx proxies to — it should never be exposed directly.

---

## 4. Create the PostgreSQL database

```bash
sudo -u postgres psql
```

Inside the `psql` prompt:

```sql
CREATE DATABASE zilard_db;
CREATE USER zilard_user WITH PASSWORD 'choose-a-strong-password-here';
ALTER ROLE zilard_user SET client_encoding TO 'utf8';
ALTER ROLE zilard_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE zilard_user SET timezone TO 'Africa/Lusaka';
GRANT ALL PRIVILEGES ON DATABASE zilard_db TO zilard_user;
\q
```

Keep the database name, user, and password — you'll put them in the `.env` file in Step 7.

---

## 5. Get the project onto the VM

Create a home for the app and copy the project in. Two common ways:

**Option A — SCP from Windows** (simplest, no Git needed): use WinSCP or `scp` from a PowerShell/WSL prompt on your Windows machine to copy the whole `you-are-an-expert-full-stack` folder to the VM, e.g.:

```powershell
scp -r "C:\Users\Director\Documents\Codex\2026-06-30\you-are-an-expert-full-stack" zilard@YOUR_VM_IP:/home/zilard/
```

**Option B — Git** (better for future updates): if the project is (or you push it to) a Git repository, clone it on the VM instead:

```bash
sudo mkdir -p /home/zilard/apps
cd /home/zilard/apps
git clone <your-repo-url> you-are-an-expert-full-stack
```

Either way, end up with the project at:

```
/home/zilard/apps/you-are-an-expert-full-stack
```

**Do not copy your local `db.sqlite3`, `.env`, or any `venv`/`.venv` folder** — those are handled separately below.

---

## 6. Create the Python virtual environment

```bash
cd /home/zilard/apps/you-are-an-expert-full-stack
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary whitenoise
```

(`psycopg2-binary` is the PostgreSQL driver; `whitenoise` serves static files efficiently even though Nginx will front the site.)

If `requirements.txt` doesn't already list `gunicorn`, `psycopg2-binary`, and `whitenoise`, add them so future deploys pick them up automatically:

```bash
pip freeze > requirements.txt
```

---

## 7. Production environment variables

Create `/home/zilard/apps/you-are-an-expert-full-stack/.env`:

```bash
nano .env
```

```ini
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=replace-with-a-freshly-generated-secret-key
DJANGO_ALLOWED_HOSTS=zilard.co.zm,www.zilard.co.zm,YOUR_VM_IP

DB_ENGINE=postgres
POSTGRES_DB=zilard_db
POSTGRES_USER=zilard_user
POSTGRES_PASSWORD=the-password-you-set-in-step-4
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

Generate a fresh secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Lock the file down:

```bash
chmod 600 .env
```

**Important:** `settings.py` reads these via plain `os.getenv()`, which only sees variables actually exported into the shell's environment — it will NOT automatically read `.env` just because the file exists. Systemd loads it automatically in production (via `EnvironmentFile=` in the service file, set up in Step 11), but whenever you run `manage.py` commands by hand (like the `migrate`/`loaddata` steps below), export it into your shell first:

```bash
set -a
source .env
set +a
```

Do this once per shell session before running any `manage.py` command, or your commands will silently fall back to `settings.py`'s SQLite/debug defaults instead of Postgres.

### Update `config/settings.py`

Your `settings.py` already reads its configuration from environment variables natively via `os.getenv()` (no `python-decouple` needed, and no full rewrite required) — you only need two small, targeted additions. Do NOT paste explanatory sentences like this one into the file; only the code blocks below belong in `settings.py`.

**1. Add the whitenoise middleware**, right after `"django.middleware.security.SecurityMiddleware",` in the existing `MIDDLEWARE` list:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "core.middleware.MobileApiCorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.CurrentUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

**2. Add whitenoise's storage backend and production security settings**, right after the existing static/media block:

```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
```

Verify the file still parses before running any `manage.py` command:

```bash
python -c "import ast; ast.parse(open('config/settings.py').read())" && echo "settings.py OK"
```

Copy these two edits back into your working copy of the project (Windows machine or repo) too, so they aren't lost on the next deploy.

---

## 8. Migrate your data from SQLite to PostgreSQL

Do this **on your Windows machine first**, using your existing local SQLite database (the one with your seeded website content, team members, and any DLDMS records already entered):

```powershell
cd "C:\Users\Director\Documents\Codex\2026-06-30\you-are-an-expert-full-stack"
.venv\Scripts\activate
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e sessions.Session --indent 2 > zilard_data.json
```

Copy `zilard_data.json` to the VM (SCP, same as the project folder), placing it at `/home/zilard/apps/you-are-an-expert-full-stack/zilard_data.json`.

On the VM, with the venv active and `.env` in place:

```bash
cd /home/zilard/apps/you-are-an-expert-full-stack
source venv/bin/activate
python manage.py migrate
python manage.py loaddata zilard_data.json
```

If `loaddata` complains about integrity errors on a fresh database, run `migrate` first (as above) so all tables exist, then retry `loaddata`.

**If you'd rather start clean on the VM instead of migrating existing data** (e.g. this is a first real deployment and the local data was only for testing), skip the dump/load and instead run on the VM:

```bash
python manage.py migrate
python manage.py seed_website
python manage.py createsuperuser
```

---

## 9. Collect static files and media

```bash
cd /home/zilard/apps/you-are-an-expert-full-stack
source venv/bin/activate
python manage.py collectstatic --noinput
```

If you migrated data via `loaddata` rather than reseeding, also copy your **media** folder (team photos, slideshow images) from the Windows machine to the VM, since `loaddata` only restores database rows, not the actual image files:

```powershell
scp -r "C:\Users\Director\Documents\Codex\2026-06-30\you-are-an-expert-full-stack\media" zilard@YOUR_VM_IP:/home/zilard/apps/you-are-an-expert-full-stack/
```

---

## 10. Create a superuser (if you haven't already)

```bash
python manage.py createsuperuser
```

---

## 11. Run Gunicorn as a systemd service

Create a socket-backed systemd service so Gunicorn starts on boot and restarts on failure.

```bash
sudo nano /etc/systemd/system/zilard.socket
```

```ini
[Unit]
Description=gunicorn socket for ZILARD

[Socket]
ListenStream=/run/zilard.sock

[Install]
WantedBy=sockets.target
```

```bash
sudo nano /etc/systemd/system/zilard.service
```

```ini
[Unit]
Description=gunicorn daemon for ZILARD
Requires=zilard.socket
After=network.target

[Service]
User=zilard
Group=www-data
WorkingDirectory=/home/zilard/apps/you-are-an-expert-full-stack
EnvironmentFile=/home/zilard/apps/you-are-an-expert-full-stack/.env
ExecStart=/home/zilard/apps/you-are-an-expert-full-stack/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/zilard.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

(`config.wsgi:application` assumes your settings module is `config/settings.py` per your project layout — adjust if different.)

Start and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl start zilard.socket
sudo systemctl enable zilard.socket
sudo systemctl status zilard.socket
```

Test it's alive:

```bash
curl --unix-socket /run/zilard.sock localhost
```

You should get back raw HTML (or a Django error page if something's misconfigured — check with `sudo journalctl -u zilard.service` if so).

---

## 12. Configure Nginx as the reverse proxy

```bash
sudo nano /etc/nginx/sites-available/zilard
```

```nginx
server {
    listen 80;
    server_name zilard.co.zm www.zilard.co.zm YOUR_VM_IP;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/zilard/apps/you-are-an-expert-full-stack/staticfiles/;
    }

    location /media/ {
        alias /home/zilard/apps/you-are-an-expert-full-stack/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/zilard.sock;
    }
}
```

Enable the site and disable the default:

```bash
sudo ln -s /etc/nginx/sites-available/zilard /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

At this point, visiting `http://YOUR_VM_IP` (or the domain, once DNS is pointed) should show the ZILARD homepage, and `http://YOUR_VM_IP/app/` should reach the internal DLDMS login.

---

## 13. Add HTTPS with a real certificate

Only do this once your domain's DNS A record points at the VM's IP.

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d zilard.co.zm -d www.zilard.co.zm
```

Certbot edits the Nginx config automatically to redirect HTTP → HTTPS and sets up auto-renewal. Confirm renewal works:

```bash
sudo certbot renew --dry-run
```

---

## 14. Verify everything works

Go through this checklist from a browser:

- Homepage loads with logo, slideshow, and the beaded flag-color border rails
- About page shows team photos correctly, governance section centered with no odd gaps
- Publications/News/Research pages load and detail pages open
- Contact form submits successfully
- `/admin/` logs in with your superuser and shows all website content (Home slides, Team members, News, Publications, etc.)
- `/app/` reaches the internal DLDMS login and, once logged in, dashboards/workers/reports/feedback all work
- Static assets (CSS, images) and media (photos) load over HTTPS with no mixed-content warnings

---

## 15. Ongoing maintenance

**Deploying an update** (after copying new/changed files to the VM, e.g. via `git pull` or SCP):

```bash
cd /home/zilard/apps/you-are-an-expert-full-stack
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart zilard.service
```

**Database backups** — schedule a nightly cron job:

```bash
sudo -u postgres pg_dump zilard_db > /home/zilard/backups/zilard_$(date +%F).sql
```

Set this up via `crontab -e` for the `zilard` user, and periodically copy backups off the VM (to your Windows machine or cloud storage) rather than relying on the VM's own disk alone.

**Media backups** — the `media/` folder (team photos, slide images, any uploaded files) isn't in the database dump; back it up separately, e.g. with `rsync` to another machine.

**Logs** — check `sudo journalctl -u zilard.service -f` for Gunicorn/Django errors, and `/var/log/nginx/error.log` for Nginx-level issues.

---

## Troubleshooting quick reference

| Symptom | Likely cause | Check |
|---|---|---|
| 502 Bad Gateway | Gunicorn not running / socket path wrong | `sudo systemctl status zilard.service`, `sudo journalctl -u zilard.service` |
| Static files (CSS/images) missing, site looks unstyled | `collectstatic` not run, or Nginx `alias` path wrong | `python manage.py collectstatic --noinput`; check the `/static/` block path matches `STATIC_ROOT` |
| Team photos / slideshow images missing | `media/` folder not copied to VM, or Nginx `/media/` alias wrong | Confirm files exist under `media/team/` and `media/slides/` on the VM |
| `DisallowedHost` error | Domain/IP not in `DJANGO_ALLOWED_HOSTS` | Update `.env`, restart `zilard.service` |
| Can't connect to Postgres | Wrong credentials in `.env`, or Postgres not running | `sudo systemctl status postgresql`, re-check `.env` values against Step 4 |
| Changes not showing after redeploy | Gunicorn workers still running old code | `sudo systemctl restart zilard.service` |

---

*Replace `zilard.co.zm`, `YOUR_VM_IP`, and the placeholder passwords throughout with your actual imbra VM details before running these commands.*
