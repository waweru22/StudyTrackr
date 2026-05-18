# StudyTrackr — Group Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- pip

## Backend Setup

1. `cd` into the `backend` folder
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate it:
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and fill in `DATABASE_URL`
   (get the Supabase connection string from the project lead — **do NOT run the seeder yourself**)
6. Verify your connection:
   ```
   python check_db.py
   ```
   - If it says **"ready"** → you're good to go
   - If it says **"empty"** → contact the project lead

## Running the Backend

```
flask run
```
or
```
python run.py
```

## Frontend Setup

1. `cd` into the `frontend` folder
2. Install dependencies:
   ```
   npm install
   ```
3. Start the dev server:
   ```
   npm run dev
   ```

## IMPORTANT — Who Runs What

| Action | Who |
|--------|-----|
| `flask db upgrade` | **Project lead only** (once, against Supabase) |
| `python -m app.utils.seeder` | **Project lead only** (once, after migrations) |
| `python check_db.py` | **Everyone** (to verify your connection) |
| `flask run` / `npm run dev` | **Everyone** (daily development) |

> **Group members NEVER need to run `flask db upgrade` or the seeder.**
> If data is missing, run `python check_db.py` and report the output to the project lead.

## Demo User Credentials

| User | Email | Password | Level | Template |
|------|-------|----------|-------|----------|
| Ernest | 20221192@nileuniversity.edu.ng | 1234567 | 300 | Deep Work |
| Ameer | 20220088@nileuniversity.edu.ng | 1234567 | 200 | Pomodoro |
