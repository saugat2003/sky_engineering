# Django Docker Setup

## Prerequisites
- Docker
- Docker Compose

## Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd <project-directory>
```

2. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

3. **Access the application**
- Application: http://localhost:8000
- Admin panel: http://localhost:8000/admin

## Docker Commands

```bash
# Build the image
docker build -t django-app .

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop containers
docker-compose down
```

## File Structure
```
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```