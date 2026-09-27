# TaskFlow - Hairdrama Tech Assignment

A simple task management application built for the Hairdrama Tech internship assignment.

## Technology

* **Frontend:** Next.js + TypeScript + plain CSS
* **Backend:** Flask + Python
* **Database:** Supabase PostgreSQL
* **Authentication:** Google OAuth 2.0 through Supabase Auth
* **Email:** Gmail SMTP with Gmail App Password
* **Deployment:** Vercel (frontend) + Render (backend)

## Architecture

```text
                         Google
                           |
                       OAuth 2.0
                           |
                           v
Browser -> Next.js Frontend -> Flask REST API -> Supabase PostgreSQL
              |                    |
              |                    v
              |               Gmail SMTP
              |                    |
              |                    v
              |              Email notifications
              |
              v
        Supabase Auth
```

### Why this design?

* **Next.js** handles the user interface and Google sign-in flow.
* **Flask** handles API requests, authentication verification, authorization, business logic, and database access.
* **Supabase Auth** handles Google authentication and user sessions.
* **Supabase PostgreSQL** stores application users and tasks.
* **Gmail SMTP** sends task notification emails.
* The **Supabase secret key and Gmail credentials stay only on the backend**.

## Main Features

1. Sign in with Google.
2. Automatically create or update the application user after login.
3. Create tasks.
4. Assign a task to another registered user.
5. View tasks created by you or assigned to you.
6. Mark assigned tasks as completed.
7. Send an email when a task is created.
8. Send an email when a task is completed.
9. Deployed frontend and backend.

---

# 1. Supabase Setup

Create a Supabase project.

Run:

```text
migrations/001_initial_schema.sql
```

in the Supabase SQL Editor.

The database contains two main tables:

### `users`

Stores application user information:

* `id`
* `email`
* `name`
* `avatar_url`
* `created_at`

The user ID references the authenticated user from Supabase Auth.

### `tasks`

Stores:

* `id`
* `title`
* `description`
* `created_by`
* `assigned_to`
* `status`
* `created_at`
* `completed_at`

The task status is restricted to:

```text
pending
completed
```

Indexes are also created for `created_by` and `assigned_to`.

Row Level Security is enabled on the application tables. Database access in this application is performed through the Flask backend using the server-side Supabase secret key.

---

# 2. Google OAuth Setup

Enable Google authentication from:

```text
Supabase Dashboard
→ Authentication
→ Providers
→ Google
```

Configure the Google Client ID and Client Secret.

The Google OAuth flow is:

```text
User clicks Continue with Google
              |
              v
       Supabase OAuth
              |
              v
            Google
              |
              v
      Google authenticates user
              |
              v
      Supabase creates session
              |
              v
       /auth/callback
              |
              v
          Dashboard
```

The frontend starts the OAuth flow using:

```typescript
supabase.auth.signInWithOAuth({
  provider: "google",
  options: {
    redirectTo: `${window.location.origin}/auth/callback`,
  },
});
```

The callback page checks whether a valid session exists and redirects the user to the dashboard.

---

# 3. Authentication Flow

After Google login, the frontend gets the current Supabase session.

The access token is sent to the Flask backend using:

```text
Authorization: Bearer <access-token>
```

The Flask backend reads this token and asks Supabase Auth to verify it.

```text
Next.js
   |
   | Authorization: Bearer token
   v
Flask API
   |
   | Verify token
   v
Supabase Auth
   |
   v
Authenticated User
```

Protected backend endpoints use this authentication mechanism.

The application also synchronizes the authenticated user with the application's own `users` table through:

```text
POST /api/users/sync
```

The backend uses an **upsert**, meaning:

* If the user doesn't exist → create the user.
* If the user already exists → update the user.

---

# 4. Gmail Setup

A Gmail account with 2-Step Verification is used for sending application emails.

Create a Gmail App Password and store it in the backend environment variables.

Do not commit the real password to GitHub.

The application uses:

```text
smtp.gmail.com
Port: 465
SSL
```

The email flow is:

```text
Flask Backend
      |
      v
Create EmailMessage
      |
      v
Connect to Gmail SMTP
      |
      v
SSL connection
      |
      v
Authenticate with Gmail App Password
      |
      v
Send Email
```

The backend uses the Gmail address and App Password only on the server.

---

# 5. Backend Setup

Open a terminal:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy:

```text
.env.example
```

to:

```text
.env
```

and configure the required backend environment variables.

Run the Flask application:

```bash
python app.py
```

The local backend runs on:

```text
http://localhost:5000
```

The health endpoint is:

```text
/api/health
```

For production, Render runs the application using:

```bash
gunicorn app:app
```

---

# 6. Backend Environment Variables

The backend uses the following environment variables:

```text
SUPABASE_URL=
SUPABASE_SECRET_KEY=
FRONTEND_URL=
PORT=
GMAIL_ADDRESS=
GMAIL_APP_PASSWORD=
```

### Important

`SUPABASE_SECRET_KEY` and `GMAIL_APP_PASSWORD` are server-side secrets.

They must never be exposed in the frontend or committed to GitHub.

---

# 7. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend runs on:

```text
http://localhost:3000
```

Copy:

```text
.env.example
```

to:

```text
.env.local
```

and configure the frontend environment variables.

---

# 8. Frontend Environment Variables

The frontend uses:

```text
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=
```

The Supabase URL and browser-safe public/anon key are used to create the Supabase browser client.

The backend API URL tells the frontend where the Flask API is running.

The frontend does **not** contain the Supabase secret key or Gmail App Password.

---

# 9. Main API Endpoints

## Authentication

### Sync User

```text
POST /api/users/sync
```

Creates or updates the authenticated user's application record.

### List Users

```text
GET /api/users
```

Returns registered users that can be selected as task assignees.

---

## Tasks

### List Tasks

```text
GET /api/tasks
```

Returns tasks created by or assigned to the authenticated user.

### Create Task

```text
POST /api/tasks
```

Creates a new task and sends an email notification to the assigned user.

### Complete Task

```text
PATCH /api/tasks/<task_id>/complete
```

Marks an assigned task as completed and sends an email notification to the task creator.

---

# 10. Create Task Flow

```text
User enters task details
          |
          v
Next.js sends POST /api/tasks
          |
          v
Access token added as Bearer token
          |
          v
Flask verifies authenticated user
          |
          v
Validate title and assignee
          |
          v
Create task in PostgreSQL
          |
          v
Send email to assignee
          |
          v
Return 201 Created
```

The `created_by` value comes from the authenticated backend user rather than being trusted from the frontend.

This prevents the client from pretending that another user created the task.

---

# 11. Complete Task Flow

```text
Assigned user clicks Complete
          |
          v
PATCH /api/tasks/<id>/complete
          |
          v
Authenticate user
          |
          v
Find task
          |
          v
Check current user == assigned_to
          |
      ┌───┴───┐
      |       |
     YES      NO
      |       |
      v       v
Update     403 Forbidden
task
      |
      v
Set completed_at
      |
      v
Find task creator
      |
      v
Send completion email
```

The backend performs the authorization check even though the frontend only displays the completion button to the assigned user.

This is because frontend restrictions are not a security boundary.

---

# 12. Email Flow

### When a task is created

```text
Task saved
    |
    v
Find assignee
    |
    v
Gmail SMTP
    |
    v
Email sent to assignee
```

### When a task is completed

```text
Task updated
    |
    v
Find task creator
    |
    v
Gmail SMTP
    |
    v
Email sent to creator
```

Email delivery is handled after the database operation. If email delivery fails, the task operation itself is not rolled back.

---

# 13. Project Structure

```text
TaskFlow/
│
├── frontend/
│   ├── app/
│   │   ├── auth/
│   │   │   └── callback/
│   │   │       └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── lib/
│   │   ├── api.ts
│   │   └── supabase.ts
│   │
│   └── .env.example
│
├── backend/
│   ├── routes/
│   │   ├── auth.py
│   │   └── tasks.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   └── email_service.py
│   │
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
│
├── migrations/
│   └── 001_initial_schema.sql
│
└── README.md
```

---

# 14. Important Backend Design Decisions

### Authentication

The backend does not trust the frontend to identify the current user.

It verifies the Supabase access token before performing protected operations.

### Authorization

For completing a task, the backend checks:

```text
task.assigned_to == authenticated_user.id
```

If not, it returns:

```text
403 Forbidden
```

### Error Handling

The API uses appropriate HTTP status codes:

```text
200 → Successful request
201 → Resource created
400 → Invalid request
401 → Not authenticated
403 → Not authorized
404 → Resource not found
```

### Database Access

The Supabase client is created once and reused by the backend.

### Task Listing

The task API retrieves:

* Tasks created by the current user
* Tasks assigned to the current user

It then merges them by task ID to avoid duplicates and adds creator/assignee information to the response.

---

# 15. Deployment

## Backend

The Flask backend is deployed on **Render**.

The backend root directory is:

```text
backend
```

Production start command:

```bash
gunicorn app:app
```

The required backend environment variables are configured in the Render dashboard.

The production frontend URL is configured in:

```text
FRONTEND_URL
```

This is also used for Flask CORS configuration.

## Frontend

The Next.js frontend is deployed on **Vercel**.

The production environment variables are configured in the Vercel project settings:

```text
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
NEXT_PUBLIC_API_URL
```

The production frontend communicates with the deployed Flask backend through `NEXT_PUBLIC_API_URL`.

---

# 16. Production Health Check

The Flask backend provides:

```text
GET /api/health
```

A successful response is:

```json
{
  "status": "ok",
  "message": "TaskFlow API is running"
}
```

This endpoint is useful for confirming that the deployed backend is running.

---

# 17. Security Notes

* Google passwords are never handled by the application.
* Google authentication is handled through Supabase Auth.
* Access tokens are sent using the `Authorization: Bearer` header.
* Backend verifies access tokens before protected operations.
* `created_by` is determined from the authenticated backend user.
* Task completion is authorized on the backend.
* Supabase secret credentials stay on the backend.
* Gmail App Password stays on the backend.
* Real `.env` files should never be committed to GitHub.
* `.env.example` contains only variable names/placeholders.

---

# 18. Deployment Status

The application is currently deployed with:

```text
Frontend → Vercel
Backend  → Render
Database → Supabase PostgreSQL
Auth     → Supabase Google OAuth
Email    → Gmail SMTP
```

The production application supports:

* Google login
* User synchronization
* Task creation
* Task assignment
* Task listing
* Task completion
* Creation email notification
* Completion email notification

---

# 19. Git Commit History

The project uses small feature-based commits where appropriate.

Examples:

```text
chore: initialize project

feat: add supabase task schema

feat: add flask task api

feat: add google authentication

feat: add task dashboard

feat: add gmail notifications

feat: add google login icon

chore: add production config
```

---

# Interview Summary

The complete architecture can be summarized as:

```text
Next.js
   ↓
User Interface
   ↓
Supabase Auth
   ↓
Access Token
   ↓
Flask REST API
   ↓
Authentication + Authorization
   ↓
Supabase PostgreSQL
   ↓
Task Data
   ↓
Gmail SMTP
   ↓
Email Notifications
```

The main design principle is:

> **The frontend handles the user experience, while the backend is responsible for authentication verification, authorization, business logic, and secure database operations.**
