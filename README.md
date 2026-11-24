# AI Travel Planner Agentic

An AI-assisted trip planner with a FastAPI backend, PostgreSQL persistence, SQLAlchemy async ORM, Alembic migrations, JWT authentication, and a React/Vite TypeScript frontend. Geoapify validates trip starting locations and destinations; Google Places API (New) verifies itinerary attractions and restaurants; Gemini organizes itineraries.

## Location verification and itinerary flow

Trip creation validates dates, then independently geocodes the starting location and destination with Geoapify before saving. Trip edits repeat Geoapify verification for any changed location. Canonical names, formatted addresses, coordinates, and available Geoapify place IDs are stored on the trip. The authenticated `POST /locations/verify` endpoint remains available for Google Places lookups. Itinerary generation verifies the saved destination, searches for nearby attractions and restaurants within 25 km, and gives those verified records to Gemini. Every itinerary activity must reference a returned attraction Place ID, and food recommendations can reference only returned restaurant Place IDs. The backend rejects invented or repeated place references and replaces displayed names/addresses with Google Places values.

Location verification and Gemini are independent services. Missing credentials, quota limits, timeouts, and upstream failures return service errors; none are treated as proof that a location is invalid, and no trip is saved after a verification failure. Geoapify and Google Places credentials are only read by the backend.

Trip create/update and itinerary generation enforce a start date of today or later using `APP_TIMEZONE` (default `Asia/Kolkata`). The frontend date controls use the matching `VITE_APP_TIMEZONE` setting and disable past dates.

## Configuration

1. Copy the root `.env.example` to `.env`. Set database and JWT settings for your environment. The backend also loads `backend/.env` when running locally; Docker Compose passes both optional files to the container, with `backend/.env` taking precedence if a variable appears in both.
2. Set `GEOAPIFY_API_KEY` in `backend/.env` for server-side trip location validation. Set `GEOAPIFY_TIMEOUT_SECONDS` only if you need to change the default 8-second timeout. Never put this key in frontend variables.
3. In Google Cloud, enable billing and **Places API (New)**, create a server-side API key, restrict it to Places API (New), and set `GOOGLE_PLACES_API_KEY`. `GOOGLE_MAPS_API_KEY` is accepted as a fallback for itinerary discovery and the standalone verification endpoint.
4. Set `GEMINI_API_KEY` to enable itinerary generation. Set `APP_TIMEZONE` to a valid IANA timezone; keep frontend `VITE_APP_TIMEZONE` in sync.
5. Configure allowed browser origins with `CORS_ORIGINS` when deploying outside the local defaults.

The frontend `.env.example` contains `VITE_API_BASE_URL` and `VITE_APP_TIMEZONE`.

## Start locally on Windows

From the repository root, install the backend dependencies and migrate the database:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

In another terminal:

```powershell
Set-Location frontend
Copy-Item .env.example .env
npm ci
npm run dev
```

The Vite development server prints its local URL (normally `http://localhost:5173`). The backend API and interactive docs are normally at `http://localhost:8000` and `http://localhost:8000/docs`.

## Start with Docker Compose

Configure the root `.env` or `backend/.env` first, then rebuild and recreate the backend so updated API routes and settings are used:

```powershell
docker compose up --build -d --force-recreate backend
docker compose exec backend alembic upgrade head
```

The Compose stack starts PostgreSQL and the backend. The Vite frontend is started separately using the frontend steps above. Logs and shutdown:

```powershell
docker compose logs -f backend
docker compose down
```

Secret `.env` files are excluded from the Docker build context and supplied to the container as runtime environment variables.

## API endpoints

- `POST /locations/verify` — authenticate and verify a destination with Google Places.
- `POST /trips` — create a trip after date and destination verification.
- `GET /trips`, `GET /trips/{trip_id}` — list and retrieve owned trips.
- `PUT /trips/{trip_id}` — update a trip; destination changes are re-verified.
- `DELETE /trips/{trip_id}` — delete an owned trip.
- `POST /trips/{trip_id}/generate-itinerary` — verify destination and attractions, generate with Gemini, validate, and persist.
- `GET /trips/{trip_id}/itinerary` — retrieve the saved itinerary.
- `GET /itineraries` — list saved itinerary metadata.

Trip and itinerary endpoints retain the existing JWT authentication and ownership checks. Invalid destination responses use:

```json
{
  "success": false,
  "error": "INVALID_LOCATION",
  "message": "The entered destination could not be verified. Please enter a valid location."
}
```

## Database migrations

The new migration `20261119_0005` adds nullable destination Place ID, canonical name, formatted address, and coordinates. Existing trips remain readable; a destination must pass current Places verification before a new itinerary can be generated.

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m alembic downgrade -1
```

## Tests

```powershell
Set-Location backend
$env:PYTHONPATH = "."
..\.venv\Scripts\python.exe -m unittest discover -s tests -v
Set-Location ..\frontend
npm test
npm run build
```

Unit tests cover date boundaries, invalid versus unavailable Google Places results, quota classification, Gemini provider errors, and validation of AI attraction references. Live Jaipur/Paris verification and live itinerary generation require configured Google and Gemini credentials and are not mocked by the unit suite.
