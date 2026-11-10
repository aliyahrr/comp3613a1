# Student Awards Test Planning

## User Acceptance Test Plan

The UAT scenarios below follow the screens and transitions in the Student Awards
wireframe. Run them in the application and record observed results; do not mark a
test as passed based on the Postman collection alone.

![Student Awards workflow board](wireframes/wireframes.png)

### Test setup

- The supplied run used `bob` as the student and `admin` for review.
- Before the captured submission, Bob's dashboard showed 2 approved hours and 12 lifetime hours.
- The student submitted 4 hours; after admin approval, the dashboard showed 6 approved hours and 16 lifetime hours.
- The prize shop showed the $50 Amazon Giftcard at 10 hours, the T-shirt out of stock, and the Waterbottle at 3 hours.

### UAT cases

| ID | Wireframe screen / flow | User task | Expected result / acceptance criteria | Actual result | Outcome |
|---|---|---|---|---|---|
| UAT-01 | Sign in | Sign in as `bob`. | Student Awards opens with student navigation, including My Hours and Prizes. | Screenshot shows the login form with username `bob`; authenticated screenshots show “Welcome, bob” and the student navigation. | Pass |
| UAT-02 | Workflow 1: My Hours → Submit hours | Submit volunteer hours with an activity, completion date, and proof file. | Submission appears in My Hours as Pending; approved balance does not change until review. | Form screenshot shows Animal Shelter, 4 hours, a completion date, and `matrix.pdf`. My Hours then shows Animal Shelter, 4.0 hours, Pending, while the approved balance remains 2.0. | Pass |
| UAT-03 | Workflow 2: Pending Approvals → Reviewing | Sign in as `admin`, open the pending submission, inspect it, and approve it. | Submission is approved; approved and lifetime totals increase by the submitted 4 hours. | Admin's Pending approvals screenshot lists Bob's Animal Shelter submission for 4.0 hours. The later My Hours screenshot shows it Approved, with approved hours changing from 2.0 to 6.0 and lifetime hours from 12.0 to 16.0. | Pass |
| UAT-04 | Workflow 2: Reviewing → Reject without comment | Leave the rejection comment blank and select Reject. | Rejection is blocked with a required-comment message; the review remains available for correction. | Review screenshot shows the blank comment field and the alert “A comment is required when rejecting a submission.” | Pass |
| UAT-04a | Workflow 2: Reviewing → Reject with comment | Add a rejection comment to a pending submission and select Reject. | Submission is marked Rejected, the comment is retained, and approved balance does not increase. | The screenshot sequence shows the admin entering “proof is blurry” for Bob's 2-hour “Planting trees” submission and rejecting it; the student confirmed the rejection workflow passed. | Pass |
| UAT-05 | Workflow 3: Prizes | As `bob`, open Prizes with 6 approved hours and inspect the T-shirt. | Current approved hours show 6; the T-shirt is out of stock and cannot be redeemed. | Prize-shop screenshot shows current approved hours 6.0 and the T-shirt marked “Out of stock”; giftcard and Waterbottle options are available. | Pass |
| UAT-06 | Workflow 3: Insufficient-hours screen | Select the $50 Amazon Giftcard, which costs 10 hours. | The shortfall screen says 4 more approved hours are needed and offers a path back to prizes or to submit hours; no redemption occurs. | Screenshot states “Need 4.0 more approved hours to claim $50 Amazon Giftcard” and shows Submit hours and Back to prizes options. | Pass |
| UAT-07 | Workflow 3: Redeem confirmation | Select Waterbottle (cost: 3 hours), then choose Cancel. | Student returns to the catalog; balance remains 6 and stock is unchanged. | The screenshot sequence shows the Waterbottle confirmation with cost 3 hours and balance after 3.0 hours, followed by cancellation back to the prize shop; the student confirmed the cancel workflow passed. | Pass |
| UAT-08 | Workflow 3: Redeem confirmation → Success / QR receipt | Confirm a Waterbottle redemption after reviewing the confirmation. | Success screen shows remaining balance 3 and a QR receipt; redemption succeeds. | Success screenshot shows Waterbottle, remaining balance 3.0 hours, a QR code, and a receipt code. | Pass |

## Unit Test Plan

Focus areas:

- VolunteerHoursService.submit_hours rejects invalid inputs.
- The hours form rejects non-positive values before entering the service.
- VolunteerHoursService.review_submission approves only Pending items and enforces rejection comments.
- PrizeService.redeem_prize prevents empty stock and insufficient hours.
- Prize redemption updates both the user balance and prize stock.

## Integration Test Plan

Validate end-to-end behaviour via FastAPI TestClient:

- create a student account and log in
- submit volunteer hours with a valid proof upload
- review the submission as an admin
- redeem a prize with enough approved hours
- confirm all database states match expectations

## Test execution

Run the suite with:

```bash
pytest -q
```
