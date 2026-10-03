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
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose-prod.yml
├── .env.example
└── .gitignore
```

## Getting started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Start with Docker

```bash
cp .env.example .env
docker compose up --build
```

The application will be available at:

| Service       | URL                          |
|---------------|------------------------------|
| React frontend | http://localhost:5173        |
| Django API    | http://localhost:8000/api/   |
| Django admin  | http://localhost:8000/admin/ |

When using `docker-compose.yml`, the migration `0002_seed_test_users` creates the test users defined in `backend/api/migrations/0002_seed_test_users.py`. Their password is `123456`; for example:

| Username   | Email                    | Role          |
|------------|--------------------------|---------------|
| `admin`    | `admin@matacartas.es`    | Administrator |
| `cervantes`| `cervantes@complutum.es`| Normal user   |
| `lope`| `lope@madrid.es`| Normal user   |
| `garcilaso`| `garcilaso@toledo.es`| Normal user   |
| `quevedo`| `quevedo@cr.es`| Normal user   |
| `gongora`| `gongora@cordoba.es`| Normal user   |

### Create a superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

The command asks for `username`, `email`, `nombre` and `password`. The new user is created with `is_staff=True` and `is_superuser=True`.

The production compose file only applies migration `0001_initial`, so it does not create the test users automatically.

## Development

### Running Django tests

```bash
docker compose exec backend python manage.py test
```

### Running Locust load tests

Prepare the test users and games first:

```bash
docker compose exec backend python manage.py preparar_locust
```

Copy the generated game IDs into `PARTIDA_IDS` in `backend/api/tests/locustfile.py` if they differ from the configured values. Then start Locust:

```bash
docker compose exec backend locust \
	-f api/tests/locustfile.py \
	--host http://localhost:8000 \
	--web-host 0.0.0.0
```

Open http://localhost:8089 to select the test user class and configure the load. The prepared credentials are `locust_user` / `locust_password` and `locust_player_1` through `locust_player_32`, each with password `locust_password_N`.

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

NOTE: There are variables required for deployment and mail services that are not shown in the table. These variables are: `FRONTEND_URL`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`.
