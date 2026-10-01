# Notes

## Requirements

- **Docker & Docker Compose** (for containerized setup)
- **Python**: `>= 3.12` (would also work in older versions as well)
- **Package Manager for Python**:
  - `uv` (recommended): [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
    or
  - `pip` (standard way)
- **Node.js**: `>= 24` with `npm` (would also work in older versions as well)

---

## How to Run

### Method 1: Docker Compose (Quickest / Recommended)

Starts both the backend (port `8000`) and the frontend (port `5173`):

```bash
# Build and start all services in detached mode
docker compose up --build -d

# Open the app in your browser:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000

# Stop containers when finished
docker compose down
```

---

### Method 2: Manual Local Setup

#### 1. Backend

Navigate to `backend`:

```bash
cd backend
```

**Option A: Using `uv` (Fastest)**

```bash
# Install dependencies
uv sync

# Seed the database with 20 sneakers
uv run python -m db.seed

# Start FastAPI development server
uv run fastapi dev main.py
```

**Option B: Using `pip` and virtual environment**

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database
python -m db.seed

# Start FastAPI server
fastapi dev main.py
```

The backend will be available at `http://localhost:8000`.

#### 2. Frontend

In a separate terminal, navigate to `frontend`:

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Running the Concurrency Simulation

To run the concurrent load test verifying zero overselling and correct waitlist queuing:

```bash
cd backend

# Realistic mode (simulates human delay and ~80% payment conversion)
uv run python simulate.py --mode realistic --users 27

# Realistic mode with no abandonment means 100% payment conversion
uv run python simulate.py --mode realistic --users 100 --pay-ratio 1

# Burst mode (all users hit /buy at the exact same millisecond)
uv run python simulate.py --mode burst --users 100
```
