# AI Travel Planner

This repository contains the production-oriented foundation for an AI Travel Planner. The backend currently provides only platform concerns: configuration, logging, middleware, exception handling, and system status endpoints. It contains no authentication, database models, migrations, AI agents, workflows, business logic, or frontend pages.

## Technology direction

- Backend: Python 3.13, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, LangChain, and LangGraph
- Frontend: Next.js, React, TypeScript, Tailwind CSS, and shadcn/ui
- Platform: Docker and Docker Compose

## Repository layout

```text
.
├── backend/
│   ├── alembic/                 # Future database migration package
│   ├── docker/                  # Backend container definitions
│   ├── src/
│   │   ├── application/         # Use cases and application-facing contracts
│   │   ├── core/                # FastAPI configuration and runtime concerns
│   │   ├── domain/              # Pure business concepts and rules
│   │   ├── infrastructure/      # Implementations for external technologies
│   │   ├── presentation/        # Delivery-layer adapters, such as HTTP
│   │   └── main.py              # Reserved composition root; intentionally empty
│   └── tests/                   # Backend test suite, mirroring source boundaries
├── frontend/
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── app/                 # Reserved Next.js route structure; no pages yet
│   │   ├── components/          # Reusable UI building blocks
│   │   ├── features/            # Feature-oriented frontend modules
│   │   ├── hooks/               # Reusable React hooks
│   │   ├── lib/                 # Client-side utilities and integrations
│   │   ├── services/            # Client-side service boundaries
│   │   ├── stores/              # Client state boundaries
│   │   ├── styles/              # Global styling and design tokens
│   │   └── types/               # Shared TypeScript types
│   └── tests/                   # Frontend tests
├── .env.example                 # Safe environment-variable template
├── .gitignore                   # Generated files and local secrets to exclude
├── docker-compose.yml           # Reserved local service orchestration file
└── requirements.txt             # Backend dependency manifest
```

## Backend folders

`backend/alembic/` is reserved for Alembic migration configuration. `versions/` will hold individual revision files when persistence is introduced.

`backend/docker/` holds backend-specific container artifacts, keeping deployment concerns outside application source.

`backend/src/core/` contains the FastAPI application factory, typed environment profiles, logging setup, and the settings loader.

`backend/src/domain/` is the innermost Clean Architecture layer. It will contain business entities, value objects, domain services, repository abstractions, domain events, and domain-specific exceptions. It must not depend on frameworks or infrastructure.

`backend/src/application/` coordinates domain behavior. `commands/`, `queries/`, and `use_cases/` reserve separate write, read, and orchestration flows; `dto/` holds data-transfer boundaries; `ports/` defines interfaces implemented by outer layers; `services/` holds application-level coordination.

`backend/src/infrastructure/` contains framework and vendor implementations. Its folders separate runtime configuration, SQLAlchemy/PostgreSQL persistence, Redis caching, LangChain/LangGraph integrations, messaging, and third-party service clients.

`backend/src/presentation/` contains inbound delivery adapters. The API layer currently contains only the root, health, and versioned status routes, plus their transport-level dependencies, middleware, and exception handlers. `cli/` remains reserved for non-HTTP operational entry points.

`backend/tests/` is organized by architectural layer so unit, integration, and end-to-end tests remain clearly scoped.

## Frontend folders

`frontend/public/` stores static files served by Next.js.

`frontend/src/app/` reserves the Next.js App Router location. It deliberately has no route, layout, or page implementation.

`frontend/src/components/` separates generic shared components, feature-composed components, and `ui/` primitives reserved for shadcn/ui.

`frontend/src/features/` groups future user-facing capabilities by business feature, preventing pages from accumulating cross-feature logic.

`frontend/src/hooks/`, `lib/`, `services/`, `stores/`, `styles/`, and `types/` respectively reserve reusable hooks, generic utilities, API/client boundaries, client state, styling primitives, and TypeScript contracts.

`frontend/tests/` is reserved for frontend test code.

## Current status

The backend foundation is implemented and exposes only `GET /`, `GET /health`, and `GET /api/v1/status`. The next implementation step should be chosen explicitly after approval.

## Complete folder reference

| Folder | Purpose |
| --- | --- |
| `backend/` | Backend workspace and Python service boundary. |
| `backend/alembic/` | Future Alembic migration package. |
| `backend/alembic/versions/` | Future individual migration revisions. |
| `backend/docker/` | Backend container artifacts. |
| `backend/src/` | Backend source root and future composition boundary. |
| `backend/src/core/` | FastAPI factory, settings profiles, logging, and runtime configuration. |
| `backend/src/domain/` | Framework-independent business rules. |
| `backend/src/domain/entities/` | Future domain entities. |
| `backend/src/domain/value_objects/` | Future immutable domain concepts. |
| `backend/src/domain/repositories/` | Future repository abstractions. |
| `backend/src/domain/services/` | Future domain services. |
| `backend/src/domain/events/` | Future domain events. |
| `backend/src/domain/exceptions/` | Future domain-specific exceptions. |
| `backend/src/application/` | Use-case coordination layer. |
| `backend/src/application/commands/` | Future write-side commands. |
| `backend/src/application/queries/` | Future read-side queries. |
| `backend/src/application/use_cases/` | Future application workflows. |
| `backend/src/application/dto/` | Future cross-layer data-transfer contracts. |
| `backend/src/application/ports/` | Future interfaces for outer-layer implementations. |
| `backend/src/application/services/` | Future application coordination services. |
| `backend/src/infrastructure/` | Technology and vendor implementations. |
| `backend/src/infrastructure/config/` | Future runtime configuration adapters. |
| `backend/src/infrastructure/persistence/` | Future SQLAlchemy/PostgreSQL adapters. |
| `backend/src/infrastructure/cache/` | Future Redis adapters. |
| `backend/src/infrastructure/llm/` | Future LangChain provider integrations. |
| `backend/src/infrastructure/graph/` | Future LangGraph workflow integrations. |
| `backend/src/infrastructure/messaging/` | Future messaging adapters. |
| `backend/src/infrastructure/external/` | Future external-service clients. |
| `backend/src/presentation/` | Inbound delivery adapters. |
| `backend/src/presentation/api/` | Reserved FastAPI transport boundary. |
| `backend/src/presentation/api/exceptions/` | HTTP exception handlers and error-response formatting. |
| `backend/src/presentation/api/routers/` | Future route modules. |
| `backend/src/presentation/api/schemas/` | Future HTTP request/response contracts. |
| `backend/src/presentation/api/dependencies/` | Future transport dependency wiring. |
| `backend/src/presentation/api/middleware/` | Future HTTP middleware. |
| `backend/src/presentation/cli/` | Future command-line adapters. |
| `backend/tests/` | Backend test root. |
| `backend/tests/unit/` | Future fast, isolated tests. |
| `backend/tests/integration/` | Future technology-integration tests. |
| `backend/tests/e2e/` | Future end-to-end tests. |
| `frontend/` | Frontend workspace and Next.js application boundary. |
| `frontend/public/` | Future static assets. |
| `frontend/src/` | Frontend source root. |
| `frontend/src/app/` | Reserved Next.js App Router structure. |
| `frontend/src/components/` | Reusable UI component root. |
| `frontend/src/components/ui/` | Future shadcn/ui primitives. |
| `frontend/src/components/shared/` | Future shared presentational components. |
| `frontend/src/components/features/` | Future feature-composed components. |
| `frontend/src/features/` | Future business-feature modules. |
| `frontend/src/hooks/` | Future reusable React hooks. |
| `frontend/src/lib/` | Future frontend utilities. |
| `frontend/src/services/` | Future frontend service boundaries. |
| `frontend/src/stores/` | Future client-state boundaries. |
| `frontend/src/styles/` | Future global styles and design tokens. |
| `frontend/src/types/` | Future TypeScript contracts. |
| `frontend/tests/` | Frontend test root. |
