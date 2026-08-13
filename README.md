# career-semantic

        Classification, extraction, similarity, retrieval, and grounded context.

        Modules:

        - `classify-extract`
- `embed-similarity`
- `retrieve-rag`

        Every module accepts `{"module": "...", "input": {...}, "run_id": "optional"}`
        through `POST /v1/run`; `GET /healthz` reports readiness. The runtime is deterministic and
        has no network or model dependency. `coverage.json` contains only capability IDs and an
        immutable corpus snapshot ID—never private job-posting text or MongoDB identifiers.

        ```bash
        uv sync --extra dev
        uv run pytest
        uv run ruff check .
        docker compose up --build
        ```
