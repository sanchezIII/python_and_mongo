# Flask + MongoDB API – Quick Docker Setup

This project is a Flask REST API backed by MongoDB. The entire stack (app, database and Mongo-Express GUI) can be brought up with **one Docker Compose command**.

---

## Prerequisites

- Docker 20.10+
- Docker Compose v2 (comes bundled with modern Docker Desktop)

> **No local Python, Poetry or MongoDB installation required.** Everything runs inside containers.

---

## 1 — Clone the repository

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

---

## 2 — Environment variables (optional)

`docker-compose.yml` already ships with sensible defaults:

```yaml
MONGODB_URI=mongodb://admin:password@mongodb:27017/flask_db?authSource=admin
PORT=5001          # host port exposed for the API (container port 5000)
API_KEYS=demo-api-key-12345      # comma-separated list accepted by the gateway
```

If you need to customise anything, copy `.env.example` to `.env` and tweak the values; Docker Compose automatically picks them up.

---

## 3 — Build & start the stack

```bash
# build images (only first time) and start in background
docker compose up --build -d
```

Containers launched:

| Service         | Image             | Host port | Purpose                     |
| --------------- | ----------------- | --------- | --------------------------- |
| `app`           | flask+poetry      | `5001`    | Python API (Gunicorn/Flask) |
| `mongodb`       | `mongo:7`         | `27017`   | MongoDB database            |
| `mongo-express` | `mongo-express:1` | `8081`    | Web UI for MongoDB          |

Wait a few seconds, then verify the health-check:

```bash
curl http://localhost:5001/health
```

Expected JSON:

```json
{ "status": "healthy", "version": "v1", "database": "connected" }
```

---

## 4 — Using the API

All endpoints live under `/api` and require an API Key header:

```bash
curl -H "X-API-Key: demo-api-key-12345" http://localhost:5001/api/customers
```

Main resources:

- `/api/customers`
- `/api/products`
- `/api/subscribe` ▶️ create full subscription
- `/api/analytics/financial-metrics` ▶️ business KPIs

See `docs/FRONTEND_API_GUIDE.md` for a full list.

---

## 5 — Run automated tests (inside the container)

```bash
# open an interactive shell
docker exec -it flask-app bash

# inside the container
poetry run pytest -v
```

---

## 6 — Stopping & removing containers

```bash
docker compose down      # stop & remove
```

---

## 7 — Troubleshooting

| Symptom                           | Fix                                                   |
| --------------------------------- | ----------------------------------------------------- |
| `connection refused` on port 5001 | `docker compose ps` – is the `app` container healthy? |
| MongoDB auth errors               | Double-check `MONGO_INITDB_ROOT_USERNAME/PASSWORD`    |
| 401 Unauthorized from API         | Provide `X-API-Key` header (see _step 4_)             |

---

### Credits

Created for technical evaluation purposes. MIT License.
