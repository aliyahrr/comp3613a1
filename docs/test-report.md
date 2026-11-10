# Test Reporting

## Summary

The test suite covers the Student Awards services, FastAPI routes, cookie authentication, and the Postman workflow collection. The Postman collection uses the actual form and JSON endpoints, including login, volunteer-hours submission, admin review, prize redemption, and receipt/QR routes.

## Automated validation

Command run:

```bash
pytest -q
```

Result:

```text
9 passed, 1 warning
```

The Postman/Newman collection passed against local Uvicorn both with redirects
disabled at `http://127.0.0.1:8000` and with Postman's default redirect-follow
behavior at `http://127.0.0.1:5000`:

```text
requests:     18
test-scripts: 18
assertions:   18
failed:        0
```

The runs after reset were preceded by `python manage.py init`. The reset check
confirmed that seeded IDs and balances returned to their initial values, and
that submissions and redemptions were empty.

Separate test-file runs captured:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_services.py -q
3 passed, 1 warning in 0.21s

.\.venv\Scripts\python.exe -m pytest tests\test_routes.py -q
6 passed, 1 warning in 0.39s
```

The warning in both runs is Starlette's deprecation warning about using
`httpx` with `starlette.testclient`; it did not fail either test run.

## User Acceptance Testing

The wireframe-based UAT outcomes are recorded in [docs/test-plans.md](test-plans.md).
The submitted screenshots show the student login, hours submission and pending
status, admin pending review and approval, the 6-hour prize catalog, the
4-hour giftcard shortfall, the required-comment validation, and the Waterbottle
success/QR receipt. The screenshot sequences also show the comment entered
before rejection and the Waterbottle confirmation followed by canceling back
to the prize shop. These UAT cases are recorded as passed. Postman results
remain separate API-level evidence.

## Artifacts

- `tests/test_services.py`
- `tests/test_routes.py`
- `docs/postman/student-awards-api.postman_collection.json`
- `tests/fixtures/proof.pdf`
