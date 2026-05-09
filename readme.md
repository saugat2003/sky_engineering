# Broadcast Engineering Team Registry (Django)

## Prerequisites
- Python 3.10+
- pip

## Project Setup (Local)

1. Clone the repository and move into the project folder.

```bash
git clone <repository-url>
cd group_project
```

2. Create and activate a virtual environment.

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Apply database migrations.

```bash
python manage.py migrate
```

5. Start the development server.

```bash
python manage.py runserver
```

## Access the App
- Application: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Common Commands

Create a superuser:

```bash
python manage.py createsuperuser
```

Run tests:

```bash
python manage.py test
```

Collect static files (if needed):

```bash
python manage.py collectstatic
```

Static assets are collected into `staticfiles/`. User uploads live under `media/` and are served separately under `/media/`.

## Main Structure

```text
accounts/
config/
home/
messaging/
organization/
scheduling/
teams/
templates/
requirements.txt
manage.py
```