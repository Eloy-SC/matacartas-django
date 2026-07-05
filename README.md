# matacartas_django

A starter project with a **Django** REST API backend, **React** (Vite) frontend, **PostgreSQL** database, and **Docker** for containerisation.

## Stack

| Layer     | Technology                       |
|-----------|----------------------------------|
| Backend   | Django 4.2 + Django REST Framework |
| Frontend  | React 18 + Vite                  |
| Database  | PostgreSQL 15                    |
| Container | Docker + Docker Compose          |

## Project structure

```
matacartas_django/
├── backend/                 # Django project
│   ├── api/                 # REST API app (models, views, urls, tests)
│   ├── matacartas/          # Django project settings & URLs
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React + Vite app
│   ├── src/
│   │   ├── App.js
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   ├── nginx.conf           # Used in production image
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Getting started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd matacartas_django
cp .env.example .env
# Edit .env and set a strong SECRET_KEY for production
```

### 2. Build and start services

```bash
docker compose up --build
```

This will:
- Start a PostgreSQL 15 database on port `5432`
- Run Django migrations and start the API on port `8000`
- Start the React dev server with hot-reload on port `5173`

### 3. Open the app

| Service       | URL                          |
|---------------|------------------------------|
| React frontend | http://localhost:5173        |
| Django API    | http://localhost:8000/api/   |
| Django admin  | http://localhost:8000/admin/ |

### 4. Create a Django superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

## Development

### Running Django tests

```bash
# With Docker (uses PostgreSQL)
docker compose exec backend python manage.py test

# Without Docker (uses SQLite in-memory)
cd backend
python manage.py test --settings=matacartas.test_settings
```

### Running Locust load tests

```bash
cd backend
locust -f api/tests/locustfile_user.py --host http://localhost:8000
locust -f api/tests/locustfile_partida.py --host http://localhost:8000
locust -f api/tests/locustfile_rango.py --host http://localhost:8000
```

Por defecto usa el usuario normal `cervantes/123456` para los endpoints de usuario y partida, y `admin/123456` para los endpoints de administración. Puedes sobrescribirlos con `LOCUST_USERNAME`, `LOCUST_PASSWORD`, `LOCUST_ADMIN_USERNAME`, `LOCUST_ADMIN_PASSWORD` y `LOCUST_PARTIDA_PRIVADA_CLAVE`.

### Running the backend without Docker

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Set environment variables or create a .env file in backend/
python manage.py migrate
python manage.py runserver
```

### Running the frontend without Docker

```bash
cd frontend
npm install
npm run dev
```

## Environment variables

See `.env.example` for all available variables.

| Variable              | Default                         | Description                    |
|-----------------------|---------------------------------|--------------------------------|
| `SECRET_KEY`          | insecure default                | Django secret key              |
| `DEBUG`               | `True`                          | Django debug mode              |
| `ALLOWED_HOSTS`       | `localhost,127.0.0.1`           | Comma-separated allowed hosts  |
| `POSTGRES_DB`         | `matacartas`                    | Database name                  |
| `POSTGRES_USER`       | `postgres`                      | Database user                  |
| `POSTGRES_PASSWORD`   | `postgres`                      | Database password              |
| `POSTGRES_HOST`       | `db`                            | Database host (Docker service) |
| `POSTGRES_PORT`       | `5432`                          | Database port                  |
| `CORS_ALLOWED_ORIGINS`| `http://localhost:5173,...`     | Allowed CORS origins           |