# Sky Engineering Team Registry

A Django web application for managing engineering teams, departments, and related collaboration workflows such as messaging and scheduling.

## Features
- Team and department registry with skills, ownership, and dependencies
- Account onboarding and profile-driven dashboard views
- Internal messaging flows (compose, mailbox, detail)
- Scheduling views (monthly calendar, meeting detail)
- Admin panel for data management

## Tech Stack
- Python 3.10+
- Django 6.0.1
- SQLite for local development
- PostgreSQL supported via `psycopg2-binary`
- Pillow for image uploads (avatars)

## Project Structure
```text
accounts/       # auth, registration, profiles
config/         # Django settings and URLs
department/     # department registry
home/           # dashboard and landing views
messaging/      # internal messages
scheduling/     # meeting scheduling
teams/          # team registry and dependencies
templates/      # HTML templates
static/         # source static assets
staticfiles/    # collected static assets
media/          # user uploads
manage.py
requirements.txt
seed.py
```

## Prerequisites
- Python 3.10+
- pip

## Local Setup
1. Create and activate a virtual environment.

Windows (PowerShell):
```powershell
python -m venv .venv
\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.
```bash
pip install -r requirements.txt
```

3. Apply database migrations.
```bash
python manage.py migrate
```

4. (Optional) Seed the database with sample data.
```bash
python seed.py
```
The seed script resets the database and creates demo users, teams, and dependencies. The default password for seeded users is `Password123!`.

5. Start the development server.
```bash
python manage.py runserver
```

## Access the App
- Application: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Configuration
Set the following environment variables for production deployments:

```text
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-user
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@example.com
```

For local development, the email backend defaults to console output.

## Database
The default configuration uses SQLite (`db.sqlite3`). A PostgreSQL configuration template is included in [config/settings.py](config/settings.py) and can be enabled by setting the `DATABASES` block accordingly.

## Common Commands
Create a superuser:
```bash
python manage.py createsuperuser
```

Run tests:
```bash
python manage.py test
```

Collect static files (for production):
```bash
python manage.py collectstatic
```

### Makefile (Optional)
If you have GNU Make available, use the shortcuts below:
```bash
make run
make migrate
make makemigrations
make superuser
make test
```
`make lint` and `make format` require `flake8` and `black` installed.

## Static and Media
- Static assets are served from `/static/` and collected into `staticfiles/`.
- User uploads live under `/media/` and are stored in the `media/` directory.

## Deployment Notes
- Set `DEBUG=False` and a strong `SECRET_KEY`.
- Configure `ALLOWED_HOSTS` and email settings.
- Run `python manage.py collectstatic`.
- Ensure media storage is backed by persistent storage (for example, a mounted volume or object storage).