# NYC 311 Analytics Bot

An AI-powered analytics assistant for exploring NYC 311 service request data. Ask natural language questions about complaint types, resolution times, geographic patterns, and get instant insights powered by LLMs.

## Features

- **Natural Language Queries** - Ask questions in plain English, get SQL-powered answers
- **Intelligent Guardrails** - Automatic filtering of malicious and irrelevant prompts
- **Professional Analysis** - Structured responses with insights and data visualization
- **Multi-Agent Workflow** - LangGraph-powered pipeline: Guardrail → SQL Generator → Executor → Responder
- **Secure by Design** - Read-only database access with SQL injection protection

## Prerequisites

- Python 3.14+
- PostgreSQL 14+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenRouter API key

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd null-axis-assignment
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Activate virtual environment**
   ```bash
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

## Database Setup

1. **Create PostgreSQL database**

   ```bash
   createdb nyc311
   ```

2. **Run schema migration**

   ```bash
   psql -d nyc311 -f data/database.sql
   ```

3. **Import CSV data** (364,559 records)
   ```bash
   psql -d nyc311 -c "
   COPY service_requests (
       unique_key, created_date, closed_date, agency, agency_name, complaint_type,
       descriptor, location_type, incident_zip, incident_address, street_name,
       cross_street_1, cross_street_2, intersection_street_1, intersection_street_2,
       address_type, city, landmark, facility_type, status, due_date,
       resolution_description, resolution_action_updated_date, community_board,
       borough, x_coordinate, y_coordinate, park_facility_name, park_borough,
       school_name, school_number, school_region, school_code, school_phone_number,
       school_address, school_city, school_state, school_zip, school_not_found,
       school_or_citywide_complaint, vehicle_type, taxi_company_borough,
       taxi_pick_up_location, bridge_highway_name, bridge_highway_direction,
       road_ramp, bridge_highway_segment, garage_lot_name, ferry_direction,
       ferry_terminal_name, latitude, longitude, location
   )
   FROM '$(pwd)/data/311_Service_Requests_from_2010_to_Present.csv'
   WITH (FORMAT CSV, HEADER true, NULL '');
   "
   ```

## Configuration

1. **Copy environment file**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**

## Running the Application

```bash
streamlit run src/app.py
```

The application will be available at `http://localhost:8501`

## Example Queries

Try asking questions like:

- "What are the top 10 complaint types by number of records?"
- "For the top 5 complaint types, what percent were closed within 3 days?"
- "Which ZIP code has the highest number of complaints?"
- "What proportion of complaints include a valid latitude/longitude?"
- "Which agency has the slowest average resolution time?"

## Project Structure

```
.
├── src/
│   ├── app.py                      # Streamlit web interface
│   ├── main.py                     # CLI entry point for testing
│   ├── workflow.py                 # LangGraph workflow orchestration
│   ├── models.py                   # Pydantic models for structured outputs
│   ├── settings.py                 # Environment configuration
│   ├── states.py                   # LangGraph state definitions
│   └── system-prompts/
│       ├── guardrail_prompt.md     # Security & relevance validation
│       ├── query_writer_prompt.md  # SQL generation instructions
│       └── responder_prompt.md     # Response formatting guidelines
├── data/
│   ├── database.sql                # PostgreSQL schema
│   └── 311_Service_Requests_*.csv  # NYC 311 dataset
├── pyproject.toml                  # Project dependencies
└── README.md                       # This file
```

## Data Schema

The `service_requests` table contains 53 columns including:

- **Identifiers**: `unique_key`
- **Dates**: `created_date`, `closed_date`, `due_date`
- **Agency**: `agency`, `agency_name`
- **Complaint**: `complaint_type`, `descriptor`
- **Location**: `borough`, `incident_zip`, `latitude`, `longitude`
- **Status**: `status`, `resolution_description`

See `data/database.sql` for complete schema with indexes.

## Technologies

- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - Multi-agent workflow orchestration
- **[LangChain](https://python.langchain.com/)** - LLM integration and tool binding
- **[Streamlit](https://streamlit.io/)** - Interactive web interface
- **[asyncpg](https://magicstack.github.io/asyncpg/)** - Async PostgreSQL driver
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation and settings
- **[OpenRouter](https://openrouter.ai/)** - LLM API aggregation

---

**Note**: This application requires an OpenRouter API key to function. You can obtain one at [openrouter.ai](https://openrouter.ai/).
