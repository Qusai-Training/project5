# Skills Utilization Platform

A full-stack web application that helps users track their skills, discover relevant courses, and receive personalized course recommendations. The platform lets users register a profile with their skills, browse a searchable course catalog, enroll in courses, and manage a membership — with recommendations driven by both keyword skill-matching and simple embedding-based similarity.

## Tech Stack

- **Backend:** Python 3, Flask, Flask-CORS
- **Database:** PostgreSQL, SQLAlchemy 2.0 (Core), Alembic migrations
- **Auth:** JWT (PyJWT) with hashed passwords (Werkzeug)
- **Frontend:** Vanilla HTML, CSS, and JavaScript (no build step)

## Project Structure

```
project5/
├── backend/
│   ├── app.py                  # Entry point (runs Flask on port 5000)
│   └── app/
│       ├── __init__.py         # App factory, blueprints, static/template serving
│       ├── config.py           # Environment-driven configuration
│       ├── db.py               # SQLAlchemy engine and shared MetaData
│       ├── models.py           # Table definitions (users, skills, courses, ...)
│       ├── errors.py           # Custom API errors + global error handlers
│       ├── init_db.py          # Create tables and seed sample data
│       ├── seed_skills.py      # Seed the skills catalog
│       ├── seed_courses.py     # Seed the course catalog
│       ├── routes/             # Flask blueprints (auth, users, courses, skills)
│       └── services/           # Business logic (auth, user, skill, course)
├── frontend/
│   ├── templates/              # login, register, courses, course-details,
│   │                           # recommendations, profile, skills
│   ├── static/                 # CSS files
│   └── js/                     # Page-specific frontend logic
└── requirements.txt
```

## Features

- **User authentication** — register, login, and password change with JWT-based session handling.
- **Skill management** — select skills at registration and add skills later from the catalog.
- **Course catalog** — paginated listing with search, skill/instructor filters, and title/relevance sorting.
- **Course details** — shows skill-match score, enrollment status, and related courses.
- **Course enrollment** — enroll directly from course details.
- **Recommendations** — personalized course suggestions ranked by skill-match score combined with vector similarity (hybrid scoring).
- **Membership** — renew and cancel memberships with automatic expiry handling.
- **Frontend served by Flask** — pages, static assets, and JS served directly from the backend.

## Database Schema

| Table | Purpose |
| --- | --- |
| `users` | User accounts, profile fields, and membership status/expiry |
| `skills` | Skills catalog |
| `user_skills` | Many-to-many link between users and skills (with proficiency level) |
| `courses` | Course catalog (title, description, instructor, skill requirements) |
| `course_vectors` | Course embeddings used for similarity-based recommendations |
| `user_enrollments` | Many-to-many link between users and courses |

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL running locally
- `venv` (optional but recommended)

### Installation

1. Clone the repository and create a virtual environment:

   ```bash
   cd project5
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create the database (adjust to match your PostgreSQL setup):

   ```bash
   createdb project5
   ```

4. Set your database URL (optional — defaults to `postgresql://postgres:0000@localhost:5432/project5`):

   ```bash
   export DATABASE_URL="postgresql://postgres:0000@localhost:5432/project5"
   export SECRET_KEY="your-secret-key"
   export JWT_SECRET_KEY="your-jwt-secret-key"
   ```

5. Initialize the database and seed sample data:

   ```bash
   cd backend
   python -m app.init_db
   ```

   Or apply migrations instead:

   ```bash
   alembic upgrade head
   python -m app.seed_skills
   python -m app.seed_courses
   ```

### Running the Application

```bash
cd backend
python app.py
```

The app runs at `http://localhost:5000` and redirects to the login page.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive a JWT |
| POST | `/api/auth/change-password` | Change the authenticated user's password |
| GET | `/api/users/me` | Get the authenticated user's profile |
| POST | `/api/users/membership/renew` | Renew membership |
| POST | `/api/users/membership/cancel` | Cancel membership |
| GET | `/api/skills` | List all skills |
| GET | `/api/user/skills` | Get the user's skills |
| POST | `/api/user/skills` | Add skills to the user |
| GET | `/api/courses` | List courses (search, filter, sort, paginate) |
| GET | `/api/courses/<id>` | Get course details + related courses |
| POST | `/api/courses` | Create a course |
| POST | `/api/courses/<id>/enroll` | Enroll in a course |
| POST | `/api/recommend` | Get personalized course recommendations |

Authenticated endpoints require an `Authorization: Bearer <token>` header.

## How Recommendations Work

Each course is embedded into a fixed 64-dimensional vector using a hashing-based token embedding of its title, description, and skill requirements. On request, a user's skills are embedded the same way, and courses are ranked by a hybrid score:

```
match_score = skill_match_score * 0.6 + embedding_similarity * 0.4
```

The skill-match score is the fraction of a course's required skills that the user already has; the embedding similarity is cosine similarity between the user's skill vector and the course vector. When embeddings are unavailable, the score falls back to skill matching alone.

## Security Notes

- Passwords are hashed with `generate_password_hash` (Werkzeug).
- JWT tokens expire after 24 hours.
- `SECRET_KEY` and `JWT_SECRET_KEY` default to dev-only values — **set them to secure values in production**.
- Inputs are validated in the auth service (email format, password length, phone digits, age range).
