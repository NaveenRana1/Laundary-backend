# FoldWell API — FastAPI backend

Minimal FastAPI backend for the FoldWell laundry frontend. In-memory
storage (no database setup needed) — swap the dicts in `main.py` for
real models when you're ready to persist data.

## Endpoints
| Method | Path                     | Auth | Description                         |
|--------|--------------------------|------|--------------------------------------|
| POST   | `/signup`                | –    | Create an account, returns a token   |
| POST   | `/login`                 | –    | Sign in, returns a token             |
| GET    | `/profile`               | ✅   | Get the current user's profile       |
| PUT    | `/profile`               | ✅   | Update name / phone / address        |
| POST   | `/booking`               | ✅   | Create a booking                     |
| GET    | `/bookings`              | ✅   | List the current user's bookings     |
| POST   | `/booking/{id}/cancel`   | ✅   | Cancel a booking                     |
| POST   | `/forgot-password`       | –    | Request a reset code (demo: returned directly, no email sent) |
| POST   | `/reset-password`        | –    | Complete the reset with the code     |

Auth uses a JWT bearer token (`Authorization: Bearer <token>`), issued
on signup/login and valid for 24 hours.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be at http://localhost:8000, with interactive docs at
http://localhost:8000/docs.

## Connecting the frontend
The React app expects `VITE_API_URL` to point here — see the frontend's
`.env` (`VITE_API_URL=http://localhost:8000` by default). CORS is
already configured for the Vite dev server's default ports
(5173, 4173).

## Moving to production
- Swap `users_db` / `bookings_db` for a real database (SQLAlchemy + Postgres/SQLite is a natural fit — the route functions are already isolated).
- Move `SECRET_KEY` into an environment variable.
- Wire `/forgot-password` to an actual email provider instead of returning the code in the response.
- Add rate limiting to `/login` and `/forgot-password`.
