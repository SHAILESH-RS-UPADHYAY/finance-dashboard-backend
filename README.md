<p align="center"><img src=".github/logo.svg" width="88" height="88" alt="Finance dashboard backend logo"></p>

# Finance Data Processing and Access Control Backend

## Overview
This is a robust, clean, and easily maintainable backend API built for a finance dashboard. It handles user authentication, role-based access control (Admin, Analyst, Viewer), and full CRUD operations for financial records.

It also provides dashboard summary APIs that aggregate and calculate insights from the financial data.

## Tech Stack
- **Framework:** Python / Flask
- **Database:** SQLite (via SQLAlchemy) - *Chosen for simplicity, zero-setup, and easy evaluation.*
- **Authentication:** JWT (JSON Web Tokens)
- **Password Hashing:** Werkzeug Security

## Features
- **User Roles:** Enforces strict role-based access to specific routes using custom middleware.
  - `Admin`: Full access (Create/Update/Delete records, Manage Users).
  - `Analyst`: View records and access dashboard summaries/trends.
  - `Viewer`: Can only view records.
- **RESTful API:** Cleanly structured endpoints.
- **Pagination & Filtering:** Efficiently fetch logs using date/type/category filters and limit results.
- **Soft Deletes:** Records are marked as deleted instead of being permanently removed from the database.

## Local Setup Instructions (For Reviewer)

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd finance-backend
```

### 2. Set up a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
There is a `.env` file required at the root of the project with the following (you can use these defaults to run it instantly):
```
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=super-secret-key-change-me-in-production
JWT_SECRET_KEY=jwt-super-secret-key-change-me
DATABASE_URI=sqlite:///finance.db
```

### 5. Seed the Database
Run the seed script to automatically create the database tables and populate it with sample users and financial records.
```bash
python seed.py
```
*Check the terminal output. It will print the sample login credentials for the Admin, Analyst, and Viewer.*

### 6. Run the Server
```bash
python run.py
```
The server will start on `http://127.0.0.1:5000`

## API Documentation

### Auth routes
- `POST /api/auth/register` (body: name, email, password)
- `POST /api/auth/login` (body: email, password) -> Returns JWT
- `GET /api/auth/me` (requires JWT)

### User Management (Admin Only)
- `GET /api/users`
- `GET /api/users/<id>`
- `PUT /api/users/<id>/role` (body: role)
- `PUT /api/users/<id>/status` (body: is_active)
- `DELETE /api/users/<id>`

### Financial Records
- `POST /api/records` (Admin only)
- `GET /api/records?type=income&page=1&per_page=10` (All roles)
- `GET /api/records/<id>` (All roles)
- `PUT /api/records/<id>` (Admin only)
- `DELETE /api/records/<id>` (Admin only - performs soft delete)

### Dashboard Summaries (Analyst & Admin)
- `GET /api/dashboard/summary` (Returns totals and net balance)
- `GET /api/dashboard/category-breakdown` (Grouped totals)
- `GET /api/dashboard/recent` (All roles can access)

## Thought Process & Design Decisions
1. **SQLite over Postgres/MySQL:** For an assessment, the reviewer should be able to run the code immediately without installing a database server.
2. **Modular Structure:** Breaking down routes using Flask Blueprints (`auth.py`, `records.py`, etc.) keeps the codebase clean and maintainable.
3. **Soft Deletes:** Financial data should rarely be permanently deleted. Added an `is_deleted` flag for audit purposes.
4. **Custom Decorator:** Built a customized `@role_required` wrapper to ensure role-based logic isn't copied and pasted into every route.
