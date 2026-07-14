<div align="center">
  <img src="https://img.icons8.com/color/96/000000/radar.png" alt="Radar Icon" width="80" />
  <h1 align="center">Competitor Intelligence Monitor AI</h1>
  
  <p align="center">
    <strong>Fully automated AI Agent that tracks competitors, calculates weekly deltas, and delivers executive briefings.</strong>
  </p>

  <p align="center">
    <a href="https://github.com/avuzmal/competitor.intelligence.monitor.ai/actions"><img src="https://img.shields.io/github/actions/workflow/status/avuzmal/competitor.intelligence.monitor.ai/ci.yml?branch=main" alt="Build Status"></a>
    <a href="https://github.com/avuzmal/competitor.intelligence.monitor.ai/stargazers"><img src="https://img.shields.io/github/stars/avuzmal/competitor.intelligence.monitor.ai" alt="Stars"></a>
    <a href="https://github.com/avuzmal/competitor.intelligence.monitor.ai/network/members"><img src="https://img.shields.io/github/forks/avuzmal/competitor.intelligence.monitor.ai" alt="Forks"></a>
    <a href="https://github.com/avuzmal/competitor.intelligence.monitor.ai/issues"><img src="https://img.shields.io/github/issues/avuzmal/competitor.intelligence.monitor.ai" alt="Issues"></a>
  </p>
</div>

<hr />

## 🌟 Overview

The **Competitor Intelligence Monitor AI** is a production-ready SaaS template built to provide high-level, automated competitive intelligence.

It orchestrates scraping competitor websites, calculating structural changes ("deltas"), analyzing those changes with LLMs (Claude), and delivering polished, actionable briefings directly to clients via Email, Slack, and a modern Web Portal.

### Key Features
- 🤖 **AI Delta Engine**: Automatically detects precise week-over-week changes in competitor websites.
- 🧠 **Claude Integration**: Synthesizes raw data into structured, strategic business insights.
- ✉️ **Multi-Channel Delivery**: Beautiful HTML emails (via Resend) and Slack Webhook integration.
- 💳 **Stripe Billing**: Built-in subscription management for B2B clients.
- 💻 **Premium Client Portal**: A Next.js 14 frontend utilizing Shadcn UI for a pristine user experience.

## 🏗 Architecture & Data Pipeline

The system is designed as an asynchronous, event-driven pipeline that moves data from raw HTML scrapes to executive summaries.

```mermaid
graph TD
    %% Define Premium Styles
    classDef external fill:#6366f1,color:#fff,stroke:#4f46e5,stroke-width:2px,rx:8,ry:8;
    classDef core fill:#3b82f6,color:#fff,stroke:#2563eb,stroke-width:2px,rx:8,ry:8;
    classDef db fill:#10b981,color:#fff,stroke:#059669,stroke-width:2px,rx:8,ry:8;
    classDef client fill:#f43f5e,color:#fff,stroke:#e11d48,stroke-width:2px,rx:8,ry:8;

    %% Orchestration
    N8N[n8n Webhook Trigger]:::external -->|Initiates Weekly Run| API(FastAPI Backend):::core

    %% Data Collection
    API -->|1. Fetch Targets| DB[(PostgreSQL)]:::db
    API -->|2. Trigger Scrape| APIFY[Apify Scraper]:::external
    APIFY -->|3. Return Raw HTML/JSON| API

    %% Delta Engine & AI
    API -->|4. Compare with Last Week| DELTA{Delta Engine}:::core
    DELTA -->|5. Extract Changes| CLAUDE[Anthropic Claude AI]:::external
    CLAUDE -->|6. Generate Insights| API

    %% Storage & Delivery
    API -->|7. Save Briefing| DB
    API -->|8a. Send Email| RESEND[Resend API]:::external
    API -->|8b. Send Slack| SLACK[Slack Webhook]:::external
    
    %% Client Portal
    USER((Client)):::client -->|Logs into Portal| NEXT[Next.js Dashboard]:::core
    NEXT -->|Fetches Data| API
    RESEND -->|Delivers Email| USER
    SLACK -->|Delivers Message| USER
```

---


## 🛠 Tech Stack

| Domain | Technology |
|---|---|
| **Backend API** | FastAPI (Python 3.11+) |
| **Frontend Portal** | Next.js 14, Tailwind CSS, Shadcn UI |
| **Database & ORM** | PostgreSQL, SQLAlchemy 2.0, Alembic |
| **Data Orchestration** | Apify Python SDK, n8n (Webhooks) |
| **AI / LLM** | Anthropic Claude SDK, Pydantic V2 (Structured JSON) |
| **Infrastructure** | Docker, Docker Compose |

---

## 🚀 Quick Start (Local Development)

The easiest way to run the entire backend stack locally is via Docker.

### 1. Clone the repository
```bash
git clone https://github.com/avuzmal/competitor.intelligence.monitor.ai.git
cd competitor.intelligence.monitor.ai
```

### 2. Environment Variables
Copy the example environment file and fill in your API keys (Apify, Anthropic, Resend, Stripe).
```bash
cp .env.example .env
```

### 3. Spin up the Backend Stack
```bash
docker compose up --build
```
The FastAPI backend will be available at `http://localhost:8000`.

### 4. Run the Frontend (Client Portal)
```bash
cd frontend
npm install
npm run dev
```
The portal will be available at `http://localhost:3000`.

---

## 🤝 Contributing

We welcome contributions! Please follow these steps to contribute:
1. Check the [Issues](https://github.com/avuzmal/competitor.intelligence.monitor.ai/issues) tab for outstanding bugs or feature requests.
2. Fork the repository.
3. Create a feature branch (`git checkout -b feature/amazing-feature`).
4. Commit your changes (`git commit -m 'Add amazing feature'`).
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a **Pull Request** using our PR template.

See `.github/PULL_REQUEST_TEMPLATE.md` for our review guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
