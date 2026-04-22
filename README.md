# 🛠️ Internal Admin System (FastAPI + React)

Hi 👋
I built this project to demonstrate how I design **real-world full-stack systems** using FastAPI and React — the kind of systems businesses actually hire freelancers to build.

This is a **production-style backend** focused on clean architecture, business workflows, auditability, and long-term maintainability.

---
## 🧰 Tech Stack
*Backend
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Pytest
*Frontend
- React (with TypeScript)
- React Query (server state management)
- Axios (API layer + interceptors)
- Ant Design (UI components)

## ✨ What this backend does

This backend helps teams manage **internal business records** (leads, tickets, tasks, etc.) with proper workflows and accountability.

With this system, you can:

* Create and manage internal records
* Assign records to users
* Move records through workflow statuses
* Track **who did what and when** via audit logs
* Restrict sensitive actions using role-based access
* Safely evolve the database using migrations
* Trust changes because core behavior is tested

I intentionally kept this backend **API-only** to focus on correctness, clarity, and backend engineering quality.

---

## 🧠 Why I built it this way

Most sample projects stop at basic CRUD.

I wanted to show how I approach **professional backend development**, so this project includes:

* Explicit business actions (assignment, status changes)
* Transaction-safe audit logging
* Clean separation of layers (API, services, models)
* Modern FastAPI + SQLAlchemy 2.0 patterns
* Dockerized PostgreSQL
* Real integration tests (not mocks)

This is the kind of structure I use when building backends for clients.

---

## 🧱 Architecture Overview

I follow a **clean, layered architecture** to keep the codebase easy to understand and extend:

```
app/
├── api/            # HTTP routes (thin controllers)
├── services/       # Business logic
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response models
├── core/           # Auth, security, configuration
├── db/             # Database session & base
└── utils/          # Shared helpers
```

### Design principles I followed

* Routers stay thin
* Business rules live in services
* Actions are explicit, not hidden in PATCH
* Auditability is built-in, not bolted on
* Boring, reliable tech > flashy tools

---

## 🔐 Authentication & Authorization

* JWT-based authentication
* Role-based access (`admin`, `staff`)
* Dependency-based authorization using FastAPI
* Centralized current-user resolution

Example:

```python
Depends(require_role("admin"))
```

This makes permissions easy to reason about and extend.

---

## 🔄 Core Features

### Records Management

* Create records
* List records with pagination & filters
* Partially update records (PATCH)
* Soft-delete design for safe lifecycle handling

### Business Actions

Instead of overloading PATCH, I modeled **explicit actions**:

* Assign a record to a user
* Change record status via a dedicated endpoint

This keeps intent clear and audit logs meaningful.

### Activity Logging (Audit Trail)

Every important action is logged automatically:

* record creation
* updates
* assignments
* status changes

Each log records:

* the action performed
* the user who performed it
* the affected entity
* timestamped history

### Admin Audit Access

* Admin-only endpoint to query activity logs
* Filter logs by entity, user, or action

---

## 🖥️ Admin Frontend (React)

To complement the backend, I built a React-based admin interface that interacts with the API and demonstrates how the system behaves in real-world usage.

This is not just a UI layer — it focuses on:
* **Correct API integration**
* **Reliable state management**
* **Handling real-world edge cases** (auth, errors, async flows)

The frontend reflects the same principles as the backend: **clarity, correctness, and maintainability over unnecessary complexity.**

### ⚙️ Frontend Highlights

* **🔐 Authentication Flow**
  * Login with JWT access + refresh tokens
  * Session persistence using `sessionStorage`
  * Automatic token refresh with request retry
  * Route protection with auth hydration
* **📊 Data Management**
  * Server-side pagination, filtering, and sorting
  * Consistent `{ items, total }` API handling
  * Debounced search inputs
  * Query-based data fetching with caching via React Query
* **🔄 Mutations & Actions**
  * Explicit actions for: record assignment, status updates, and job triggers
  * Safe mutation handling without inconsistent optimistic updates
  * Automatic UI synchronization using query invalidation
* **📁 Jobs & Async Workflows**
  * Background jobs displayed with real-time progress polling
  * Export system with secure file download handling
* **🧾 Activity Logs**
  * Filterable audit logs reflecting the backend audit system
  * Client-side validation for query inputs (e.g., UUID formats)
* **⚠️ Error Handling**
  * Backend error messages (detail) propagated directly to the UI
  * Graceful fallbacks and consistent user feedback for failed actions

### 🧱 Frontend Structure

The frontend follows a **feature-based structure** to keep code modular:

```
src/
├── features/       # Feature modules (auth, users, records, jobs, etc.)
├── lib/            # Shared logic (Axios instance, token helpers)
└── shared/         # Common UI components and global hooks
```

**Design Approach:**
* API logic is strictly separated from UI components
* Custom hooks encapsulate all data fetching and mutation logic
* Components remain "dumb" and focused on rendering and interaction
* Minimal local state; server state is handled entirely by React Query

---

## 🔁 Backend ↔ Frontend Integration

This project demonstrates full-stack coordination, not isolated layers:

* **Predictable API Consumption**: The backend provides a consistent structure, and the frontend consumes it predictably using standardized query keys.
* **Unified Auth Flow**: The JWT flow, including refresh logic and rotation, is synchronized across both layers.
* **Shared Validation Logic**: Error handling and validation rules are aligned, ensuring backend detail is surfaced accurately to the user.

I also made specific backend adjustments to ensure clean frontend integration, such as refining role enums, supporting explicit unassignment, and optimizing export URL handling.

---

## 🗄️ Database & Migrations

* PostgreSQL (Dockerized)
* SQLAlchemy 2.0 ORM
* Alembic for schema migrations
* UUID primary keys
* Soft delete support
* Timestamp mixins (`created_at`, `updated_at`)

Schema changes are versioned and safe — no manual SQL guessing.

---

## 🧪 Testing

I included **real integration tests** to validate behavior:

* FastAPI `TestClient`
* Authenticated request flows
* Real PostgreSQL database
* Tests cover:

  * app health
  * record creation & listing
  * automatic audit logging

Tests focus on **how the system behaves**, not internal implementation details.

Run tests with:

```bash
pytest -v
```

---

## 🚀 Getting Started

### 1️⃣ Start PostgreSQL using Docker

```bash
docker compose up -d
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run database migrations

```bash
alembic upgrade head
```

### 4️⃣ Start the FastAPI app

```bash
uvicorn app.main:app --reload
```

---

## 📌 Example Endpoints

| Method | Endpoint               | Description                  |
| ------ | ---------------------- | ---------------------------- |
| POST   | `/records`             | Create a record              |
| GET    | `/records`             | List records                 |
| PATCH  | `/records/{id}`        | Update record                |
| POST   | `/records/{id}/assign` | Assign record                |
| POST   | `/records/{id}/status` | Change status                |
| GET    | `/activity-logs`       | View audit logs (admin only) |
| GET    | `/health`              | Health check                 |

---

## 🧭 Where this backend fits

I designed this backend so it can easily be adapted for:

* Internal admin dashboards
* CRM systems
* Operations & workflow tools
* SaaS backends
* Custom business APIs

The goal was **reuse and extension**, not one-off code.

---

🏁 Project Status
Backend complete and tested
Frontend admin panel fully integrated
Auth system (access + refresh) implemented end-to-end
Async job workflows and exports working
Core architecture stable across both layers

---

## 👤 About the Author

I’m a backend-focused Python developer who builds **clean, reliable, and maintainable APIs** using FastAPI and PostgreSQL.

This project reflects how I structure backend systems for real clients — with clarity, safety, and long-term maintainability in mind.
