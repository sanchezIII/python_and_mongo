# Flask & MongoDB REST API 🚀

This project provides a fully containerized backend service for managing customers, products, and subscriptions. It uses Flask for the API, MongoDB for the database, and is orchestrated entirely with Docker Compose.

---

### ✨ Features

- **RESTful API**: For Customers, Products, and Subscriptions.
- **Advanced Subscriptions**: Handles trials, custom settings, and lifecycle events.
- **Financial Analytics**: Built-in endpoints for MRR, ARR, Churn Rate, and more.
- **Dockerized**: One-command setup with Docker Compose.
- **Authentication**: Secure endpoints with API Key authentication.
- **Database GUI**: Includes Mongo Express for easy database management.

---

### 🐳 Prerequisites

- **Docker** (version 20.10 or newer)
- **Docker Compose** (v2, which is included with modern Docker Desktop installations)

> **That's it!** No local Python, Poetry, or MongoDB installation is required. Everything runs inside containers.

---

## 🚀 Getting Started (3 Simple Steps)

### 1. Clone the Repository

First, clone this repository to your local machine.

```bash
git clone https://github.com/sanchezIII/python_and_mongo.git
cd python_and_mongo
```

### 2. Launch the Stack

Next, use Docker Compose to build the images and start all services in the background.

```bash
# This command will build the Flask image and start all containers.
docker compose up --build -d
```

This will launch three services:

| Service         | Host Port | Purpose                             |
| --------------- | --------- | ----------------------------------- |
| `app`           | `5001`    | The Python Flask REST API           |
| `mongodb`       | `27017`   | The MongoDB database                |
| `mongo-express` | `8081`    | A web-based GUI for managing the DB |

### 3. Verify Everything is Running

Give the containers a few seconds to initialize. You can check their status with:

```bash
docker compose ps
```

Then, check the API's health status. This confirms it can connect to the database.

```bash
curl http://localhost:5001/health
```

You should see a healthy response:

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "v1"
}
```

**Congratulations, the setup is complete!**

---

## ⚙️ How to Use the API

### Authentication

All API endpoints under `/api/` are protected and require an `X-API-Key` header. The default key for development is `demo-api-key-12345`.

**Example Request:**

```bash
curl -H "X-API-Key: demo-api-key-12345" http://localhost:5001/api/customers
```

### Main Endpoints

Here are some of the most important endpoints to get you started:

- `GET /api/customers` - List all customers.
- `GET /api/products` - List all products.
- `POST /api/subscribe` - Create a new subscription (this is the recommended endpoint).
- `GET /api/analytics/financial-metrics` - Get key business metrics (MRR, ARR, etc.).

> For a complete list of all endpoints, see the `docs/FRONTEND_API_GUIDE.md` file.

### 🗂️ Using the Database GUI

A major advantage of this setup is **Mongo Express**, a web interface to view and manage your database.

- **URL**: [http://localhost:8081](http://localhost:8081)
- **Username**: `admin`
- **Password**: `admin`

Here you can directly inspect the `customers`, `products`, and `subscriptions` collections.

---

## 🧪 Running Automated Tests

Tests are run inside the `app` container to ensure the environment is consistent.

```bash
# 1. Open an interactive shell inside the Flask container
docker exec -it flask-app bash

# 2. Once inside, run the tests using Poetry
poetry run pytest -v
```

---

## 🛑 Managing the Stack

### Stopping the Services

To stop and remove all running containers, networks, and volumes:

```bash
docker compose down
```

### Viewing Logs

If you need to check the logs for the API service:

```bash
# View live logs for the 'app' container
docker compose logs -f app
```

---

## 🔧 Configuration (Optional)

The `docker-compose.yml` file is pre-configured with sensible defaults for development. If you need to override them, you can create a `.env` file in the root directory.

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit the .env file with your custom values
# Example: Change the API port or MongoDB credentials
PORT=5002
API_KEYS=my-secret-key,another-key
```

Docker Compose will automatically load the variables from `.env`, giving them priority.

---

## 🐛 Troubleshooting

| Symptom                           | Check                                                                         |
| --------------------------------- | ----------------------------------------------------------------------------- |
| `Connection refused` on port 5001 | Run `docker compose ps` to see if the `app` container is running and healthy. |
| API returns `401 Unauthorized`    | Ensure you are providing the `X-API-Key` header with a valid key.             |
| MongoDB connection errors         | Check the `mongodb` container logs (`docker compose logs mongodb`).           |

---

### Credits

Created for technical evaluation purposes. MIT License.
