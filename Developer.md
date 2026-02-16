# Backend Developer Context — Continuation Document

## 1. Developer Profile

* **Level / Role**

  * Self-taught backend-leaning full-stack developer
  * Strong backend fundamentals; frontend is secondary
  * Past beginner phase; now operating at early–mid backend engineer level

* **Primary Languages & Frameworks**

  * **Python** (primary)
  * **FastAPI** (main web framework)
  * SQLAlchemy (Core + ORM)
  * Alembic (migrations)

* **Tools & Workflow**

  * IDEs: VS Code, PyCharm
  * Uses Git regularly (GitHub)
  * Writes tests (pytest)
  * Prefers clean project structure and separation of concerns
  * Comfortable reading stack traces and debugging deeply

* **Cloud / Platform Familiarity**

  * Google Cloud Platform (hands-on)

    * Cloud Storage
    * Firestore
    * Pub/Sub
    * Secrets
    * SDK usage
    * Logging & error handling
  * Understands cloud fundamentals, not just services
  * Comfortable deploying but Docker knowledge still upcoming

---

## 2. Technical Skills (Depth-Oriented)

### Backend Frameworks

* **FastAPI**

  * Dependency injection
  * Lifespan events (modern replacement for `on_event`)
  * Request/response models (Pydantic)
  * Proper error handling (`HTTPException`)
  * Clean router/service separation
  * Async awareness (knows when *not* to use async)

### Databases

* **PostgreSQL**

  * Solid SQL fundamentals (DDL, DML, DQL, TCL)
  * Joins, subqueries, EXISTS
  * Indexing:

    * B-tree, bitmap scans
    * Composite indexes
    * Functional indexes
    * Index-only scans
    * When indexes are ignored or harmful
  * Query analysis:

    * `EXPLAIN ANALYZE`
    * Real performance experiments on large datasets
  * Transactions:

    * ACID
    * Isolation levels
    * Serializable failures vs deadlocks
    * Row locking, `FOR UPDATE`, `SKIP LOCKED`
    * Retry logic concepts

* **SQLAlchemy**

  * Core and ORM usage
  * Session lifecycle
  * Identity map
  * `Mapped`, `mapped_column`
  * Relationships, cascades, N+1 problem and fixes
  * Proper transaction boundaries (`flush` vs `commit`)
  * Avoiding ORM-caused index breakage

* **Alembic**

  * Manual migrations
  * Autogenerate (with correct metadata import)
  * Indexes and constraints via models vs migrations
  * Resetting broken Alembic state
  * Understanding `alembic_version`
  * Schema evolution discipline

### Authentication & Security

* **JWT**

  * Access vs refresh tokens
  * Expiry, claims, determinism
  * `jti` for entropy
  * Why JWTs can accidentally be identical
* **Refresh Token System**

  * Stored as **hashes**
  * Rotation logic
  * Reuse detection
  * Theft detection reasoning
* **Password Hashing**

  * bcrypt / argon2 concepts
  * Never storing raw secrets
* **Security Discipline**

  * Fail-fast configuration
  * Hashing refresh tokens
  * Revocation handling
  * Timezone-aware datetimes

### Authorization

* **RBAC (Role-Based Access Control)**

  * Roles → permissions mapping
  * Permission enum
  * Centralized policy
  * `require_permission` dependency
* **Ownership vs Permissions**

  * RBAC at API boundary
  * Ownership checks in service layer
  * Clear separation (never mixed)
* Avoids over-engineering permission DBs prematurely

### API Design, Testing, Quality

* Clean route/service split
* Explicit error messages
* Pagination:

  * Offset vs keyset
  * Keyset pagination with timestamps
* Testing:

  * pytest
  * Test helpers (`create_user`, `login_user`, etc.)
  * Auth + permission tests
  * Tests used to *find real bugs*, not silence failures

---

## 3. Projects & Practical Work

### Internal Admin Backend (Primary Project)

* FastAPI backend with:

  * Users
  * Records
  * Activity logs
* Implemented:

  * Full auth system (JWT + refresh)
  * RBAC + ownership logic
  * SQLAlchemy models + migrations
  * Index-aware pagination
  * Redis integration (async)
* Redis usage:

  * Running via Docker
  * Lifespan-managed client
  * Dependency injection
  * Health checks
  * **Refresh token reuse detection (in progress)**
* Refactored earlier naive implementations after deeper understanding

### Other Practical Work

* Data scraping scripts
* Automation
* GCP experimentation
* Backend experimentation with performance and indexing

---

## 4. Learning Style & Preferences

* **Strong preferences**

  * System-level understanding over tutorials
  * Logic first, code second
  * Wants *why*, not just *how*
  * Prefers real examples and failure analysis
  * Comfortable with complexity if justified

* **Dislikes**

  * Overly descriptive docs without intuition
  * Shallow explanations
  * Buzzwords
  * Copy-paste solutions
  * Over-engineering too early

* **Best teaching style**

  * Step-by-step reasoning
  * Clear mental models
  * Debug-driven explanations
  * Being challenged (not spoon-fed)

---

## 5. Current Direction & Intent

* **Career Goal**

  * Backend developer (Python)
  * Backend-focused full-stack acceptable
  * Interested in real production systems

* **Current Learning Focus**

  * Async & performance
  * Redis as a systems tool (not just cache)
  * Security-aware backend design
  * Scalability fundamentals

* **Explicitly Not Wanted Right Now**

  * Frontend frameworks
  * DSA grinding
  * Over-abstract system design theory
  * Premature microservices

---

## 6. Gaps, Weak Spots & Open Threads

* **Open / In Progress**

  * Redis-backed refresh token reuse detection (implementation phase)
  * Rate limiting with Redis
  * Async DB patterns (SQLAlchemy async — postponed intentionally)
  * Background tasks & queues
  * Docker & deployment (planned later)

* **Needs More Depth Later**

  * OAuth2 beyond JWT
  * Observability (metrics, tracing)
  * Advanced concurrency patterns
  * Distributed systems concepts

---

## 7. Ground Rules for Future Assistance

* ❌ Do NOT re-explain:

  * Basic SQL
  * What FastAPI is
  * What JWT is at a high level
  * What Redis is conceptually
* ✅ Do:

  * Challenge assumptions
  * Explain trade-offs
  * Use production-grade reasoning
  * Treat me as someone who can debug and reason
* **Expected Depth**

  * Mid-level backend engineer explanations
  * Focus on correctness, not shortcuts
  * Assume comfort with code, errors, and refactors

---

**Current checkpoint:**
Redis is correctly wired via FastAPI lifespan; async Redis client works; next step was **implementing Redis-backed refresh token reuse detection** and then moving to **rate limiting**.

