# Competitor Intelligence Monitor AI

An automated Competitive Intelligence AI Agent that scrapes competitor data weekly, calculates exact changes (the "delta") compared to previous snapshots, and sends this data to an LLM to generate strategic business insights.

## Project Structure

```text
competitor-radar-core/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── config.py           # Pydantic settings
│   │   └── database.py         # DB session management
│   ├── models/                 # SQLAlchemy Database Models
│   │   ├── client.py           
│   │   ├── competitor.py       
│   │   └── snapshot.py         # Weekly data snapshot state memory
│   ├── schemas/                # Pydantic V2 Models
│   │   ├── apify.py            
│   │   └── insights.py         # Structured output format for Claude
│   ├── services/
│   │   ├── apify_service.py    # Trigger Apify scraping
│   │   ├── delta_engine.py     # Diffs new data vs old snapshot using DeepDiff
│   │   ├── data_sanitizer.py   # Cleans and flattens data for LLM context window
│   │   └── claude_service.py   # Anthropic API integration using Tool-use
│   └── api/v1/
│       ├── ingestion.py        # Trigger scrapes and save state
│       └── insights.py         # Trigger AI analysis
├── alembic/                    # DB migrations
├── .env.example                # Example environment variables
└── requirements.txt            # Python dependencies
```

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/avuzmal/competitor.intelligence.monitor.ai.git
   cd competitor-radar-core
   ```

2. **Set up the virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   Add your `APIFY_API_TOKEN` and `ANTHROPIC_API_KEY`.

4. **Initialize Database**:
   ```bash
   alembic upgrade head
   ```

5. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Phases Completed
- **Phase 1 (Foundation):** State management, Database models, Apify ingestion, Delta Engine.
- **Phase 2 (The Implication Layer):** Data sanitization, strict Pydantic JSON schemas, and Anthropic Claude integration for strategic insight generation.
