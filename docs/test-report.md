# Test Reporting

## Summary

The test suite covers the Student Awards services, FastAPI routes, cookie authentication, and the Postman workflow collection. The Postman collection uses the actual form and JSON endpoints, including login, the `POST /api/hours` resource endpoint, admin review, prize redemption, and receipt/QR routes.

## Automated validation

Command run:

```bash
pytest -q
```

Result:

```text
10 passed, 1 warning
```

The latest Postman/Newman collection run passed against local Uvicorn at
`http://127.0.0.1:5000` with redirects disabled:

```text
requests:     19
test-scripts: 19
assertions:   19
failed:        0
```

The latest run used a disposable SQLite database, seeded with `python manage.py
init`, so it did not alter the configured project database.

Separate test-file runs captured:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_services.py -q
3 passed, 1 warning in 0.21s

.\.venv\Scripts\python.exe -m pytest tests\test_routes.py -q
7 passed, 1 warning
```

The warning in both runs is Starlette's deprecation warning about using
`httpx` with `starlette.testclient`; it did not fail either test run.
Newman also emitted Node.js dependency deprecation warnings; the collection
completed with no failed requests or assertions.

## User Acceptance Testing

The wireframe-based UAT outcomes are recorded in [docs/test-plans.md](test-plans.md).
Postman screenshots document the API-level collection run; the UAT cases are
reported separately from those API results.

## Artifacts

- `tests/test_services.py`
- `tests/test_routes.py`
- `docs/postman/student-awards-api.postman_collection.json`
- `tests/fixtures/proof.pdf`
