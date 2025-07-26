# 📂 Scalable Image Import System (Google Drive → S3)

This repository contains a **multi-service backend** that bulk-imports images from a **public Google Drive folder URL** to **AWS S3** and stores their metadata in **MySQL**.  It exposes two HTTP endpoints:

| Method | Path | Description |
|-------|------|-------------|
| `POST` | `/import/google-drive` | Import all images from a public Drive folder |
| `GET`  | `/images`             | List previously imported images |

---

## 🖇️ Architecture

```
 FastAPI API (gateway)  ─┬─>  Celery worker(s)  ─┬─>  AWS S3  (images)
                        │                      └─>  MySQL   (metadata)
                        └─>  RabbitMQ (task queue)
```

Each box runs in its own Docker container and can be scaled independently (`docker compose up --scale worker=5`).  The design supports importing **10 000+ images** by streaming files and using idempotent database writes.

---

## 🚀 Quick-start (local)

> **Prerequisites**: Docker Desktop (or Podman) installed and running.

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-handle/image-import-system.git
   cd image-import-system
   ```

2. **Create an `.env` file**

   ```bash
   cp .env.sample .env
   # edit .env and provide real AWS credentials & bucket name
   ```

3. **Build and start the stack**

   ```bash
   docker compose up --build -d
   ```

4. **Run one-time DB migration** (creates the `images` table)

   ```bash
   docker compose run --rm gateway      python -c "import asyncio,common.db as d, common.models; asyncio.run(d.Base.metadata.create_all(d.engine))"
   ```

5. **Import a Google Drive folder**

   ```bash
   curl -X POST http://localhost:8000/import/google-drive         -H "Content-Type: application/json"         -d '{"folder_url": "https://drive.google.com/drive/folders/1YourFolderID"}'
   # => {"task_id": "c0123..."}
   ```

6. **Retrieve imported images**

   ```bash
   curl http://localhost:8000/images | jq
   ```

---

## 🛠️ Project layout

```
.
├── docker-compose.yml   # orchestrates all services
├── .env.sample          # copy → .env and fill secrets
├── common/              # shared SQLAlchemy models / DB engine
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── gateway/             # FastAPI HTTP service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
└── worker/              # Celery background importer
    ├── Dockerfile
    ├── requirements.txt
    ├── google.py        # Google Drive helper
    ├── storage.py       # S3 uploader
    └── tasks.py         # Celery task definition
```

---

## 📝 Detailed explanation

### 1. Gateway service (`/gateway`)

* **Framework**: FastAPI
* **Endpoints**:
  * `POST /import/google-drive` – Extracts the Drive *folder ID* from the supplied URL and enqueues a Celery task.
  * `GET /images` – Returns all rows from the `images` table.
* **Environment**: Receives DB URL, Celery broker URL and AWS creds via variables.

### 2. Worker service (`/worker`)

* **Celery** worker listening on RabbitMQ.
* **`google.py`** uses the _gdown_ library to walk a public Drive folder and download images to a temporary directory.
* Each file is **stream-uploaded** to S3 via Boto3.  Metadata is recorded with `INSERT … ON DUPLICATE KEY IGNORE` semantics for idempotency.
* Retries: Celery `acks_late=True` and `max_retries=3` provide at-least-once processing.

### 3. Database (`/common`)

* MySQL 8 with a single table `images` (`google_drive_id` primary key).
* Async SQLAlchemy engine is shared by both services (`common/db.py`).

---

## 🏗️ Production notes

| Concern | Approach |
|---------|----------|
| **Scalability** | Scale `worker` replicas; DB and S3 are fully managed services |
| **Fault tolerance** | Tasks acknowledge after success; failed attempts are retried |
| **Idempotency** | Primary key on `google_drive_id` prevents duplicates |
| **Observability** | Logs via Docker; add Prometheus/Grafana in real deployments |

---

## ✨ Extending the project

* **Dropbox support** – Implement a similar iterator in `worker/dropbox.py` and register another Celery task.
* **Filtering** – Add query params to `GET /images` and extend the SQLAlchemy query.
* **Deployment** – Adapt `docker-compose.yml` to k8s manifests or ECS task defs.

---

## 🔑 License

MIT
