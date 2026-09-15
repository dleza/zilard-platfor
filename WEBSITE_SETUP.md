# ZILARD public website -- setup & deployment

This adds a public-facing institutional website (`website` app) in front of
the existing DLDMS data-collection system. The public site now owns `/`;
the login-gated internal system has moved to `/app/` (dashboard, workers,
reports, feedback all shifted one level down -- all internal links use
Django's named-URL `{% url %}` tags, so nothing inside the internal system
had to change except two hardcoded `/workers/...` strings in
`dashboards/views.py`, which now use `reverse()`).

## 1. First run (local machine)

From the project root, with your existing virtualenv active:

```
pip install -r requirements.txt
python manage.py makemigrations website   # should report "No changes detected" -- migrations are already written
python manage.py migrate
python manage.py seed_website             # loads ZILARD's own content: themes, research portfolio, publications, team, partners, homepage slides
python manage.py createsuperuser          # if you don't already have one, to manage content in /admin/
python manage.py runserver
```

If you've already run this once before and are only picking up the newer
`HomeSlide` model (homepage carousel) or newly added slide content, you
just need:

```
python manage.py migrate
python manage.py seed_website
```

`seed_website` is safe to re-run any time -- it only fills in content that
isn't there yet (matched by slug/order), it never overwrites edits you've
made in the admin.

Visit:
- `/` -- the new public website
- `/app/` -- the existing internal DLDMS dashboard (login required, unchanged behaviour)
- `/admin/` -- manage all website content (themes, publications, research activities, projects, news, team, partners, site settings, contact messages)

## 2. What's editable without touching code

Everything a content owner needs is in Django admin under **Public Website**:

- **Thematic areas** -- the four "Our Work" pillars
- **Projects** -- time-bound programmes (dates, status, role, participants)
- **Research activities** -- the research portfolio (year, funder, status, purpose)
- **Publications** -- downloadable/linkable reports (upload a PDF to *Document*, or set *External URL* to link out)
- **News & events** -- ZILARD updates vs. media coverage, dated
- **Home slides** -- the homepage carousel; each slide is either an uploaded photo, or linked to a News & Events item (pulls its title/summary/link automatically)
- **Team members** -- board/management/staff/researchers, with photo
- **Partners** -- relationship-specific collaboration descriptions
- **Site settings** -- office address, phone, email, social links (single record)
- **Contact messages** -- enquiries submitted through the public contact form

Seed data was drawn directly from the ZILARD Company Profile and the
publicly-hosted FES/SASK reports. A few items are flagged for confirmation
before go-live (see below) -- everything else can be edited freely without
a developer.

## 3. Confirm before public launch

Per the earlier content review, these still need ZILARD's sign-off:

- Office phone/address/mobile were seeded from a 2023 report cover page and
  have not been tested as currently operational -- verify and update in
  **Site settings**.
- No email address or social-media links were seeded (ownership of the
  Facebook page found in research was not confirmed) -- add them once verified.
- Named Board of Directors members are not included (the company profile
  describes the board but doesn't name members).
- The relationship between ZILARD and ZCTU ("independent" vs. "operating
  under ZCTU") should be confirmed before final "About Us" wording.

## 4. Deploying to a real hosting environment

The project already supports Postgres via environment variables
(`DB_ENGINE=postgres`), so moving off SQLite needs no code changes.

**Environment variables to set in production:**

```
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<a long random value -- never reuse the prototype default>
DJANGO_ALLOWED_HOSTS=zilard.org,www.zilard.org
DB_ENGINE=postgres
POSTGRES_DB=zilard
POSTGRES_USER=zilard
POSTGRES_PASSWORD=<strong password>
POSTGRES_HOST=<db host>
POSTGRES_PORT=5432
```

**Static & media files:** add `whitenoise` for static files on a simple
host (`pip install whitenoise`, add
`"whitenoise.middleware.WhiteNoiseMiddleware"` to `MIDDLEWARE` right after
`SecurityMiddleware`, and run `python manage.py collectstatic`). For
uploaded media (publication PDFs, team photos, news images), use a real
object store (S3-compatible) in production rather than local disk, since
most PaaS hosts don't persist local files across deploys.

**App server:** run with `gunicorn config.wsgi:application` behind Nginx
(or the hosting platform's equivalent), rather than `runserver`.

**Suggested minimal production checklist:**

1. `DJANGO_DEBUG=false`, a real `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS` set.
2. HTTPS terminated at the load balancer/reverse proxy.
3. Postgres database, with regular automated backups stored separately from the app server.
4. `python manage.py migrate` and `python manage.py seed_website` (once) run against production.
5. `python manage.py collectstatic` run on each deploy.
6. A staging environment for testing content/design changes before they go live.
7. Multi-factor authentication for admin/staff accounts with `/admin/` access.

## 5. Accessibility

The public templates target WCAG 2.2 AA: skip-to-content link, visible
focus outlines, a keyboard-operable nav (including the mobile menu), and a
contrast-checked palette (deep green on white, charcoal body text). Run an
automated check (e.g. axe or Lighthouse) and a manual keyboard pass before
launch, and caption any video content added later.
