# Competitor Radar Core

An automated Competitive Intelligence AI Agent backend. 

This product scrapes competitor data weekly via Apify, calculates the exact changes ("delta") compared to the previous week, and sends this delta to Anthropic's Claude to generate strategic business insights. These insights are then delivered to clients as premium, mobile-responsive HTML emails via Resend.

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy 2.0 + Alembic)
- **Validation**: Pydantic V2
- **External APIs**: Apify (Scraping), Anthropic (AI), Resend (Email)
- **Containerization**: Docker & Docker Compose
- **Resilience & Observability**: Tenacity, Structlog

---

## 🚀 Running Locally with Docker Compose (Recommended)

You can spin up the entire application (FastAPI + PostgreSQL) easily with Docker Compose.

1. **Environment Variables**:
   Copy the example environment file and fill in your API keys.
   ```bash
   cp .env.example .env
   ```
   *Make sure you provide valid API keys for Apify, Anthropic, and Resend, as well as a strong `WEBHOOK_SECRET`.*

2. **Start the Stack**:
   ```bash
   docker compose up --build
   ```
   The API will be available at `http://localhost:8000`.

3. **Run Database Migrations**:
   While the containers are running, execute Alembic migrations inside the `app` container:
   ```bash
   docker compose exec app alembic upgrade head
   ```

---

## 🛠 Manual Local Setup

If you prefer to run it without Docker:

1. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or .\venv\Scripts\Activate.ps1 on Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations (SQLite default)**:
   ```bash
   alembic upgrade head
   ```

4. **Start the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 🔗 n8n Webhook Configuration

To fully automate the weekly briefings, you should set up an orchestration pipeline in n8n (or any cron-like service). 

### Setup Instructions for n8n:
1. **Cron Node**: Create a Cron/Schedule Trigger node set to run every Sunday night (e.g., `0 20 * * 0`).
2. **HTTP Request Node**:
   - **Method**: `POST`
   - **URL**: `https://<your-production-url>/api/v1/webhooks/n8n/trigger-all`
   - **Headers**:
     - `X-Webhook-Secret`: `<your-configured-WEBHOOK_SECRET>`
3. **Execute**: When triggered, the backend will securely authenticate the request, fetch all active clients and their competitors, generate the AI insights in the background, and email the reports.

If you need to test a specific client individually, use the endpoint:
`POST /api/v1/webhooks/n8n/trigger-client/{client_id}`
