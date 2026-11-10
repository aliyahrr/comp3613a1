# COMP 3613 Assignment 2: Student Awards Testing Submission

## Project Description

Student Awards is a FastAPI incentive application for tracking student volunteer
hours and exchanging approved hours for prizes. Students submit volunteer
activities with proof for admin review. Approved submissions increase the
student's spendable approved-hours balance and cumulative lifetime-hours total.
Students can browse prizes, see stock and point requirements, and redeem an
eligible prize with a receipt and QR code. Admins can approve or reject pending
submissions; a rejection requires a comment.

## Use Case Diagram

![Student Awards use-case diagram](diagrams/use-case.png)

The Student actor signs in, submits hours, views approved hours, browses prizes,
and redeems prizes. The Admin actor signs in, views pending approvals, and
reviews submissions for approval or rejection. Prize redemption includes
browsing the prize list; a points-shortfall message is a conditional extension.

## Entity Relationship Diagram

![Student Awards entity relationship diagram](diagrams/entity-relationship.png)

`reviewed_by` refers to the admin User who reviewed the submission. A
Redemption links a student to a prize and stores the hours spent and unique
receipt code.

## Application Wireframe

![Wireframe: sign-in and student hours](testing-assignment-evidence/wireframe-1.png)

![Wireframe: student submission and admin review](testing-assignment-evidence/wireframe-2.png)

![Wireframe: prize shop and shortfall](testing-assignment-evidence/wireframe-3.png)

![Wireframe: redemption confirmation and receipt](testing-assignment-evidence/wireframe-4.png)

## Test Plans

The test plans and UAT cases follow the wireframe workflows:

1. Submit volunteer hours as a student.
2. Approve or reject a submission as an admin.
3. Browse prizes and redeem one as a student.

### User Acceptance Test Record

I manually executed the following UAT cases through the Student Awards
application using the student and administrator accounts. I checked each result
against the acceptance criteria and recorded the outcome below.

**Test setup:** Student account `bob`; administrator account `admin`. Before
the captured approval, Bob had 2.0 approved hours and 12.0 lifetime hours.
The prize-shop scenarios used a 6.0-hour approved balance. The catalog showed
the T-shirt out of stock, the $50 giftcard at 10 hours, and the Waterbottle
at 3 hours.

| ID | Preconditions and test action | Acceptance criteria | Actual result, evidence, and status |
|---|---|---|---|
| UAT-01 | Sign in as student `bob`. | Student session opens with My Hours and Prizes navigation. | The student dashboard displayed My Hours and Prizes navigation. Pass. |
| UAT-02 | As `bob`, submit 4 hours for Animal Shelter with date and proof. | Submission is Pending; balance remains 2.0 before review. | The submission showed Pending and Bob's balance remained 2.0. Pass. |
| UAT-03 | As `admin`, approve Bob's pending 4-hour Animal Shelter submission. | Status becomes Approved; approved/lifetime totals increase by 4.0. | The submission became Approved; balances changed 2.0 → 6.0 and 12.0 → 16.0. Pass. |
| UAT-04 | As `admin`, reject a pending submission with comment blank. | Rejection is blocked and required-comment validation appears. | The application displayed “A comment is required when rejecting a submission.” Pass. |
| UAT-05 | As `admin`, reject Bob's 2-hour Planting trees submission with “proof is blurry”. | Rejection completes with the supplied comment. | I entered “proof is blurry” and completed the rejection. Pass. |
| UAT-06 | As `bob` with 6.0 approved hours, view the T-shirt in Prizes. | Balance is 6.0 and T-shirt availability is shown as out of stock. | The 6.0 balance and “Out of stock” label were displayed. Pass. |
| UAT-07 | As `bob`, view the $50 giftcard costing 10 hours. | Shortfall of 4.0 hours is stated; submit-hours and return options are available. | The page stated that 4.0 more hours were needed and showed both options. Pass. |
| UAT-08 | As `bob`, select the 3-hour Waterbottle and cancel confirmation. | Cancellation returns to Prizes without redeeming. | The confirmation showed the 3-hour cost and projected balance; cancel returned to Prizes without redeeming. Pass. |
| UAT-09 | As `bob`, confirm the Waterbottle redemption. | Success shows 3.0 remaining hours and receipt/QR. | The success page showed a 3.0 balance, QR code, and receipt code. Pass. |

### Unit Test Plan

Unit tests isolate service behaviour using a test database and controlled
student, admin, and prize records.

| ID | Test case | Expected result |
|---|---|---|
| UT-01 | Submit volunteer hours with a value of zero. | `VolunteerHoursService` raises a validation error stating hours must be more than zero. |
| UT-02 | Approve a pending 3.5-hour submission. | The submission becomes Approved, and the student's approved and lifetime totals each increase by 3.5 hours. |
| UT-03 | Redeem a 4-hour prize with 10 approved hours and stock of 2. | A redemption records 4 hours spent, the student's balance becomes 6 hours, and prize stock becomes 1. |

### Integration Test Plan

FastAPI `TestClient` tests exercise complete HTTP requests against an isolated
test database, including authentication, request validation, route responses,
and persisted state.

| ID | Test case | Expected result |
|---|---|---|
| IT-01 | Submit volunteer hours through the browser form with a proof upload. | The route redirects with status 303 and stores one Pending submission for the student. |
| IT-02 | Create a volunteer-hours resource through `POST /api/hours` with form fields and a proof upload. | The route returns 201 with the public resource fields and does not expose the stored proof path. |
| IT-03 | Submit zero hours through the browser form. | Request validation returns 422 and no valid submission is created. |
| IT-04 | Approve a student's pending submission as an admin. | The route redirects with status 303, the submission becomes Approved, and the student's approved balance increases. |
| IT-05 | Redeem a prize as an authenticated student with sufficient hours. | The route redirects with status 303 and prize stock decreases by one. |
| IT-06 | Request the admin page without an authenticated session. | The route returns 401 Unauthorized. |
| IT-07 | Request the admin page as an authenticated student. | The route returns 403 Forbidden. |

Run the automated plans from the repository root with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_services.py tests\test_routes.py -q
```

Reference documents supplied for this assignment:

- [COMP 3613 Test Plans](https://docs.google.com/document/d/1YQPB1vPS0SFb6tIUAxmxrSUIsj-d6u98USWzvMi4mJs/edit#heading=h.yf77zv73ijjj)
- [User Acceptance Test Plan reference](https://docs.google.com/document/d/1LIPdWA39zJCuzTgSkwTKjnaqi8Yn9STFZckn4MBsf48/edit?usp=sharing)

## Unit Tests

Test file: [tests/test_services.py](https://github.com/aliyahrr/comp3613a1/blob/main/tests/test_services.py)

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_services.py -q
```

Result: **3 passed, 1 non-failing deprecation warning.**

## Integration Tests

Test file: [tests/test_routes.py](https://github.com/aliyahrr/comp3613a1/blob/main/tests/test_routes.py)

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_routes.py -q
```

Result: **7 passed, 1 non-failing deprecation warning.**

## API Tests (Postman)

The exported collection is [student-awards-api.postman_collection.json](https://github.com/aliyahrr/comp3613a1/blob/main/docs/postman/student-awards-api.postman_collection.json).
It exercises the actual FastAPI routes and cookie-based authentication,
including invalid-hours validation, authorization, both form and JSON resource submissions, review,
redemption, receipt, and QR responses. The latest Newman run completed with
**19 assertions passed and 0 failed** against the freshly seeded disposable
database at `http://127.0.0.1:5000`.

## Implementation

The application uses FastAPI and SQLModel with a layered structure:
**routes → services → repositories → models**. Routes bind form/API input and
delegate business operations to services; repositories handle persistence.
Key implementation files: [hours API route](https://github.com/aliyahrr/comp3613a1/blob/main/app/routers/volunteer_hours.py),
[hours response schema](https://github.com/aliyahrr/comp3613a1/blob/main/app/schemas/volunteer_hours.py),
[unit tests](https://github.com/aliyahrr/comp3613a1/blob/main/tests/test_services.py),
and [integration tests](https://github.com/aliyahrr/comp3613a1/blob/main/tests/test_routes.py).
Student routes provide hours history, proof upload, prize browsing, shortfall
guidance, prize confirmation, redemption, and QR receipts. Admin routes provide
a pending-approval list and submission review. The review service enforces
Pending-only decisions and requires a comment to reject. Prize redemption
checks stock and approved balance before updating the balance and stock.

## Repository

[https://github.com/aliyahrr/comp3613a1](https://github.com/aliyahrr/comp3613a1)

## Test Reports

### Unit Test Report

![Unit test result: 3 passed](testing-assignment-evidence/unit-tests.png)

### Integration Test Report

![Integration test result: 7 passed](testing-assignment-evidence/integration-tests.png)

### Postman Collection Run Report

![Postman collection run report: authorization, health, users, and hours submission](testing-assignment-evidence/postman-run-1.png)

![Postman collection run report: hours resource API and admin review](testing-assignment-evidence/postman-run-2.png)

![Postman collection run report: prize browsing, redemption, and receipt](testing-assignment-evidence/postman-run-3.png)

The Newman report shows 19 requests, 19 test scripts, and 19 assertions with
zero failures. The screenshots are arranged in collection order and show
requests sent to `http://127.0.0.1:5000`, including the `POST /api/hours`
resource endpoint.
