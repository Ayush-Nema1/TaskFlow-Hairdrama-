# TaskFlow - Hairdrama Tech Assignment

A simple, clean task management application built for the Hairdrama Tech internship assignment.

## Technology

- Frontend: Next.js + TypeScript + plain CSS
- Backend: Flask + Python
- Database: Supabase PostgreSQL
- Login: Google OAuth 2.0 through Supabase Auth
- Email: Gmail SMTP with a Gmail App Password
- Deployment: Vercel (frontend) + Render/Railway (backend)

## Architecture

```text
                    Google
                      |
                 OAuth 2.0
                      |
                      v
Browser -> Next.js Frontend -> Flask REST API -> Supabase PostgreSQL
                                  |
                                  v
                             Gmail SMTP
                                  |
                                  v
                          Email notifications
```

### Why this design?

- Next.js handles the user interface and Google sign-in flow.
- Flask keeps business logic and database access on the server.
- Supabase stores users and tasks.
- Gmail SMTP sends task notification emails.
- The Supabase service role key stays only on the backend.

## Main features

1. Sign in with Google.
2. Automatically create/update the local user record after login.
3. Create tasks.
4. Assign a task to another registered user.
5. View tasks created by you or assigned to you.
6. Mark assigned tasks as completed.
7. Send an email when a task is created.
8. Send an email when a task is completed.

## 1. Supabase setup

Create a Supabase project.

Run `migrations/001_initial_schema.sql` in the Supabase SQL Editor.

Then go to:

`Authentication -> Providers -> Google`

Enable Google provider and add the Google Client ID and Client Secret.

For local development, add your Supabase callback URL from the Supabase dashboard. Usually it looks like:

`https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback`

For production, also add the production frontend URL in the allowed redirect URLs.

## 2. Google OAuth setup

Create OAuth credentials in Google Cloud Console.

Use the Supabase callback URL as the Google OAuth redirect URI.

The frontend sends users to Google with:

```text
Continue with Google
        |
        v
Google verifies account
        |
        v
Supabase Auth creates the session
        |
        v
Next.js receives the logged-in session
```

## 3. Gmail setup

Use a dedicated Gmail account for the project. Remove spaces from the App Password when saving it in the environment variable if Google displays it grouped with spaces.

1. Turn on 2-Step Verification for the Gmail account.
2. Create a Google App Password.
3. Put that app password in `GMAIL_APP_PASSWORD`.

Do not commit the real password.

The backend uses Gmail SMTP at `smtp.gmail.com:465` with SSL.

## 4. Backend setup

Open a terminal:

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\\Scripts\\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

For a production server, Render/Railway can run:

```bash
gunicorn app:app
```

Copy `.env.example` to `.env` and fill in your values.

Run:

```bash
python app.py
```

The backend runs on `http://localhost:5000`.

## 5. Frontend setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:3000`.

Copy `.env.example` to `.env.local` and add your Supabase URL and publishable/anon key.

## 6. Test

To test task assignment, sign in with at least two Google accounts so there is another user to assign a task to.

Backend unit tests:

```bash
cd backend
python -m unittest discover -s tests
```

The tests verify the health endpoint and protected API behavior without needing real Google/Gmail credentials.

## Important interview explanation

### Google OAuth

The application does not receive the user's Google password. Google verifies the user and Supabase Auth creates an authenticated session.

### Flask authentication

Next.js gets the Supabase access token from the current session and sends it as:

```text
Authorization: Bearer <access-token>
```

Flask asks Supabase Auth to validate that token before allowing protected operations.

### Task assignment

A task stores:

- `created_by` = the user who created the task
- `assigned_to` = the user who must complete it

### Email flow

When a task is created:

```text
Task saved -> email sent to assignee
```

When a task is completed:

```text
Task updated -> email sent to task creator
```

## Deployment

### Backend

Deploy `backend` to Render or Railway.

Set the same environment variables from `backend/.env.example` in the platform dashboard.

### Frontend

Deploy `frontend` to Vercel.

Set the same variables from `frontend/.env.example`.

Also update the backend CORS value with the production frontend URL.

## Clean commit history suggestion

Use small commits such as:

```text
chore: initialize project
feat: add supabase task schema
feat: add flask task api
feat: add google authentication
feat: add task dashboard
feat: add gmail notifications
chore: add production config
```
