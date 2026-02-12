# NYC 311 Analytics Bot

An AI-powered analytics assistant for exploring NYC 311 service request data. Ask natural language questions about complaint types, resolution times, geographic patterns, and get instant insights powered by LLMs.

## Features

- **Natural Language Queries** - Ask questions in plain English, get SQL-powered answers
- **Intelligent Guardrails** - Automatic filtering of malicious and irrelevant prompts
- **Professional Analysis** - Structured responses with insights and data visualization
- **Multi-Agent Workflow** - LangGraph-powered pipeline: Guardrail → SQL Generator → Executor → Responder
- **Secure by Design** - Read-only database access with SQL injection protection

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- OpenRouter API key

## Quick Start

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd null-axis-assignment
   ```

2. **Download the dataset**

   Download the NYC 311 Service Requests CSV from [NYC Open Data](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9) and place it in:

   ```
   data/311_Service_Requests_from_2010_to_Present.csv
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your OpenRouter API key:

   ```env
   OPENROUTER_API_KEY="your-api-key-here"
   OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
   ```

4. **Start the application**

   ```bash
   docker-compose up -d
   ```

5. **Access the application**

   Open your browser and navigate to `http://localhost`

   > **Note**: The first startup will take 2-5 minutes as the CSV data (364,559 rows) is imported into the database. Subsequent restarts are fast.

## Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f db

# Stop all services
docker-compose down

# Stop and remove all data (including database)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# Check service status
docker-compose ps
```

## Manual Installation

If you prefer to run without Docker:

### Prerequisites

- Python 3.14+
- PostgreSQL 14+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenRouter API key

### Setup

1. **Clone and install dependencies**

   ```bash
   git clone <repository-url>
   cd null-axis-assignment
   uv sync
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate      # Windows
   ```

2. **Download the dataset**

   Place the CSV file in `data/311_Service_Requests_from_2010_to_Present.csv`

3. **Setup database**

   ```bash
   createdb nyc311
   psql -d nyc311 -f db/init/01-schema.sql
   ```

4. **Import CSV data** (364,559 records)

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

5. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

6. **Run the application**

   ```bash
   streamlit run src/app.py
   ```

## Configuration

The application uses environment variables from `.env`:

### Required

- `OPENROUTER_BASE_URL` - OpenRouter API endpoint
- `OPENROUTER_API_KEY` - Your OpenRouter API key

### Optional

- `DEBUG` - Enable debug logging (default: `false`)
- `OPENROUTER_MODEL_1/2/3` - Model selection for each agent
- `DATABASE_HOST/PORT/NAME/USER/PASSWORD` - Database connection (auto-configured in Docker)

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
├── data/
│   └── 311_Service_Requests_*.csv  # NYC 311 dataset (place here before starting)
├── db/
│   └── init/
│       ├── 01-schema.sql           # PostgreSQL schema
│       └── 02-import-data.sh       # CSV import script
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
├── nginx/
│   └── nginx.conf                  # Reverse proxy configuration
├── docker-compose.yml              # Docker orchestration
├── Dockerfile                      # Application container
├── pyproject.toml                  # Project dependencies
└── README.md                       # This file
```

## Troubleshooting

### Port 80 already in use

```bash
# Change the port in docker-compose.yml
ports:
  - "80:80"  # Use port 8080 instead
```

### Database connection issues

```bash
# Check database logs
docker-compose logs db

# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up -d
```

### CSV import fails

Ensure the CSV file is placed correctly:

```bash
ls -lh data/311_Service_Requests_from_2010_to_Present.csv
```

## Data Schema

The `service_requests` table contains 53 columns including:

- **Identifiers**: `unique_key`
- **Dates**: `created_date`, `closed_date`, `due_date`
- **Agency**: `agency`, `agency_name`
- **Complaint**: `complaint_type`, `descriptor`
- **Location**: `borough`, `incident_zip`, `latitude`, `longitude`
- **Status**: `status`, `resolution_description`

See `db/init/01-schema.sql` for complete schema with indexes.

## Technologies

- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - Multi-agent workflow orchestration
- **[LangChain](https://python.langchain.com/)** - LLM integration and tool binding
- **[Streamlit](https://streamlit.io/)** - Interactive web interface
- **[asyncpg](https://magicstack.github.io/asyncpg/)** - Async PostgreSQL driver
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation and settings
- **[OpenRouter](https://openrouter.ai/)** - LLM API aggregation
- **[Docker](https://www.docker.com/)** - Containerization

---

**Note**: This application requires an OpenRouter API key to function. You can obtain one at [openrouter.ai](https://openrouter.ai/).
