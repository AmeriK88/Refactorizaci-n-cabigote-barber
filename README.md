# ✂️ Ca'Bigote Barber Shop

**A Django-powered booking and management platform for a barbershop.**

Ca'Bigote brings together online appointments, customer accounts, services, reviews, email notifications, reporting, and a customized administration experience. The public website is responsive and includes Progressive Web App (PWA) support with an offline fallback.

**Application version:** `3.5.0` *(planned release; confirm against the version configured in the repository before publishing)*

> **Project status:** Actively developed. Features and deployment behavior should be verified against the current branch before a production release.

## Overview

Ca'Bigote is designed around two complementary experiences:

- **Customers** can browse services, book appointments, manage their accounts, and interact with the barbershop online.
- **Authorized staff** can manage appointments, services, users, and reports through a customized Django administration interface.

The platform currently targets a single barbershop. Multi-location operation is not presented as an existing feature.

## Features

### Customer experience

- Online appointment booking with date and time availability checks.
- Service catalog and image gallery.
- Account registration, sign-in, and profile management.
- Appointment history and account-related actions.
- Customer reviews.
- Email-based appointment notifications and password recovery.
- Responsive interface for desktop, tablet, and mobile.
- PWA integration and an offline fallback page for supported public navigations.

> Appointment editing, cancellation rules, reminder delivery, and third-party sign-in behavior depend on the active configuration and should be confirmed during release testing.

### Administration

- Customized Django Admin using `django-admin-interface` and project-specific templates, CSS, and JavaScript.
- Light, dark, and system-aware visual themes.
- Responsive navigation, tables, filters, forms, and inline editing.
- Operational dashboard with permission-aware indicators and quick actions.
- Appointment management, including today/tomorrow views and appointment charts.
- Service and user administration.
- Daily and monthly reporting workflows, with access controlled by Django model permissions.
- Password recovery pages styled consistently with the administration interface.

**Reporting terminology:** The dashboard's **estimated booking value** represents the value of reservations, **not confirmed collected revenue**. Do not interpret it as a payment or accounting ledger.

## Technology stack

| Area | Technology |
| --- | --- |
| Backend | Python, Django 5.2.x |
| Frontend | Django templates, Bootstrap 5, custom CSS and JavaScript |
| Database | MySQL (PyMySQL integration) |
| Administration | Django Admin, `django-admin-interface` |
| Authentication | Django authentication and `django-allauth` |
| Charts and reporting | Chart.js and server-side reporting utilities |
| Static assets | Django staticfiles; production configuration uses manifest-based storage |
| PWA | Web app manifest, Service Worker, offline fallback |
| Testing | Django test suite and JavaScript/Node tests |

Additional packages and exact pinned versions are defined in `requirements.txt` and the project's JavaScript tooling, where applicable. Those files are the authoritative dependency list.

## Project layout

The Django project is organized into dedicated applications:

```text
cabigote/       # Project settings, URL configuration, deployment configuration
appointments/   # Booking, availability, and appointment administration
core/           # Shared views, utilities, dashboard statistics, and tests
products/       # Image/product gallery
reports/        # Reporting workflows
reviews/        # Customer reviews
services/       # Service catalog
users/          # User-facing account and profile functionality
templates/      # Shared and overridden Django templates
static/         # CSS, JavaScript, images, PWA resources
manage.py       # Django management entry point
```

Directory names and the presence of specific files should be checked against the checked-out branch.

## Local development

### Prerequisites

- A Python version supported by the project's installed Django release.
- MySQL and the credentials required by the project settings.
- Git.
- Node.js **only if** running the JavaScript test scripts.

### Setup

```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_DIRECTORY>

python -m venv venv
```

Activate the virtual environment:

```bash
# macOS / Linux
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Configure environment variables using the **actual settings module and deployment configuration**. Do not commit `.env` files, database credentials, email credentials, OAuth secrets, or Django's `SECRET_KEY`.

Create the MySQL database and grant an application user the required permissions. Then run:

```bash
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

By default, Django's development server is available at `http://127.0.0.1:8000/`. The admin path may be language-prefixed, for example `/es/admin/`, depending on URL configuration.


## Tests and quality checks

Run the Django checks and tests:

```bash
python manage.py check
python manage.py test
```

Run the existing Node-based test command documented in the repository's JavaScript tooling, if present. Before committing:

```bash
git diff --check
git status
```

The most recent reported validation for the password-recovery work passed **166 Django tests and 6 Node tests**. These counts are historical development results, not a guarantee of the current branch's test status; rerun the suite after changes.

## Security and permissions

Ca'Bigote relies on Django's authentication, CSRF protections, form validation, and permission framework. Recent administration work has focused on:

- Restricting dashboard indicators and queries according to model permissions.
- Protecting reporting endpoints from unauthorized access.
- Keeping report downloads read-only for GET requests.
- Requiring appropriately authorized POST requests for report changes.
- Preventing staff from seeing unauthorized quick links or sensitive dashboard data.
- Preserving CSRF and token validation in password-reset flows.
- Avoiding account enumeration in password recovery.

Security settings, HTTPS enforcement, cookie attributes, CSP, brute-force protections, backups, and third-party anti-bot integrations must be assessed in the **deployed environment**. This README does not claim that every possible protection is enabled or that the application has been independently audited.

For security issues, contact the project maintainer privately rather than publishing credentials, reset tokens, or exploit details in a public issue.

## Progressive Web App and offline behavior

The public site includes a web app manifest, a Service Worker (`sw.js`), and an offline fallback page (`/offline.html`).

The Service Worker is designed to:

- Intercept eligible **same-origin GET document navigations** only.
- Prefer the network for fresh public content.
- Show a cached offline page when a public navigation fails due to a network error.
- Avoid caching private appointment, account, or administration responses.
- Maintain a versioned offline cache and remove older generations.

**Important:** The offline fallback does **not** provide offline booking, login, or access to customer records. External stylesheets, fonts, images, and scripts are not guaranteed to work offline unless separately made available by the browser or explicitly precached.

Check language-prefixed private routes such as `/es/admin/` and `/es/accounts/` when testing Service Worker exclusions. Bump the Service Worker cache version when changing cached offline content or its cache strategy.

## Deployment

Deployment requires environment-specific configuration. At a minimum:

1. Configure production secrets, allowed hosts, database access, and email delivery.
2. Apply database migrations.
3. Collect static assets using the configured storage backend.
4. Serve the application through an appropriate production WSGI/ASGI setup and HTTPS reverse proxy or hosting platform.
5. Confirm the configured `Site` domain, especially for password-reset email links.
6. Verify language-prefixed routes, permissions, password recovery, the Service Worker, and the offline fallback in a real browser.
7. Run the complete test suite and a production security configuration check.

Useful commands:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

The deployment provider, build command, and production process configuration should come from the repository's actual deployment files. Do not use outdated Heroku, PostgreSQL, or Docker examples without verifying support.

## Release notes

### v3.5.0 — Proposed

- Refined the Django administration interface with premium light/dark styling.
- Improved dashboard navigation and permission-aware operational views.
- Hardened administration and reporting access controls.
- Optimized dashboard statistics and appointment summaries.
- Improved password-recovery pages and email templates.
- Reviewed Service Worker routing and refreshed the offline user experience.

> Mark this release as published only after the version constant, deployed changes, and final checks are confirmed. Do not describe proposed work as released before it is merged and deployed.

## Roadmap

Potential future improvements, **not commitments or currently supported capabilities**:

- Further dashboard chart and accessibility improvements.
- Broader offline asset resilience.
- Expanded reporting and export formats.
- Additional notification channels and integrations.
- Multi-location support, subject to product requirements.

## Contributing and support

For bug reports and feature requests, use the repository's issue tracker **if enabled**. Include reproduction steps, expected behavior, actual behavior, and relevant non-sensitive logs. Never include secrets or personal customer information.

For commercial or project inquiries, use the contact details published by the project owner in the repository or official website.

## License

Copyright © 2026 José Félix Gordo Castaño.

The supplied project documentation identifies **Elastic License 2.0 (ELv2)**. Consult the repository's [`LICENSE.TXT`](LICENSE.TXT) for the actual license terms. This README is informational and does not replace the license text or grant additional permissions.

**Do not assume that ELv2 is an OSI-approved open-source license.** Check the license and obtain legal advice if you intend to redistribute, host, or commercialize the software.

---

**Ca'Bigote Barber Shop** — Built with Django, for a more organized barbershop experience.
