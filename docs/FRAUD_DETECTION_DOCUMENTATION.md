# Fraud and risk detection

## Classification and safeguards

FoodShare AI currently uses deterministic rule-based risk triage. It is **not a trained machine-learning model**, has no labeled fraud-training dataset, and does not return a probability or claim accuracy. A risk score is a 0–100 queue-priority signal, not a finding of misconduct. No score automatically bans, suspends, limits, or blocks an account or donation. Authorized admins review alerts and record an outcome.

## Signals

The service evaluates donation submissions and subsequent updates/cancellations for:

- **Similar submissions:** same donor and category, within a configurable look-back window, with normalized food-name similarity over a threshold and quantity agreement within a configurable tolerance where units can be converted.
- **Implausible quantity:** supported mass units converted to kilograms exceed the configured maximum. Unknown units do not receive a fabricated comparison.
- **Repeated cancellations:** counts cancellation status-history entries for the donor over a look-back window.
- **Frequent submissions:** counts donations over a short configured window.
- **Abnormal donation activity:** counts donations over a longer configured window.
- **Repeated complaints:** counts open/reviewing complaints linked to that donor's donations. The complainant's own complaint volume is not treated as suspicious, and complaint text is not copied to an alert.

Rules contribute configurable points, signal scores are clamped to 0–100, and each detected reason is stored with a stable code plus a concise explanation. The overall service result combines donation-level and account-activity scores, capped to 100.

Default individual rule points:

| Signal | Points |
| --- | ---: |
| Unrealistic quantity | 40 |
| Similar donation | 35 |
| Repeated cancellations | 30 |
| Frequent submissions | 20 |
| Abnormal activity | 25 |
| Repeated complaints | 35 |

Default score levels: LOW below 25; MEDIUM 25–54; HIGH 55–79; CRITICAL 80–100.

## Configuration

Django reads these environment variables (defaults shown):

- `FRAUD_RISK_MEDIUM_THRESHOLD=25`
- `FRAUD_RISK_HIGH_THRESHOLD=55`
- `FRAUD_RISK_CRITICAL_THRESHOLD=80`
- `FRAUD_MAX_DONATION_KG=500`
- `FRAUD_DUPLICATE_WINDOW_HOURS=48`
- `FRAUD_SIMILARITY_THRESHOLD=0.85`
- `FRAUD_DUPLICATE_QUANTITY_DELTA=0.25`
- `FRAUD_CANCELLATION_WINDOW_DAYS=30`
- `FRAUD_REPEATED_CANCELLATION_COUNT=3`
- `FRAUD_SUBMISSION_WINDOW_HOURS=24`
- `FRAUD_FREQUENT_SUBMISSION_COUNT=10`
- `FRAUD_ABNORMAL_ACTIVITY_WINDOW_DAYS=7`
- `FRAUD_ABNORMAL_ACTIVITY_COUNT=20`
- `FRAUD_COMPLAINT_WINDOW_DAYS=90`
- `FRAUD_REPEATED_COMPLAINT_COUNT=3`
- `FRAUD_POINTS_UNREALISTIC_QUANTITY=40`
- `FRAUD_POINTS_SIMILAR_DONATION=35`
- `FRAUD_POINTS_REPEATED_CANCELLATIONS=30`
- `FRAUD_POINTS_FREQUENT_SUBMISSIONS=20`
- `FRAUD_POINTS_ABNORMAL_ACTIVITY=25`
- `FRAUD_POINTS_REPEATED_COMPLAINTS=35`

## Alert storage and lifecycle

`FraudAlert` stores actor/donation references, score and level, rule version, structured reasons, occurrence count, review status and reviewer outcome. Its deduplication key is unique while status is `OPEN` or `REVIEWING`, preventing multiple active alerts for the same defined issue. Repeated hits refresh that alert instead of adding another unresolved row; after resolution, a future detection may open a new alert.

Donation create/update/cancel invokes the separate service after the business operation. Scoring failures are logged and do not block donations. It never changes user role, activity, or permissions. Alert review writes an `AuditLog` record.

## Admin review APIs and access control

The `/api/fraud-detection/alerts/` list, detail, and review routes all enforce authenticated `ADMIN` role server-side. Donor/NGO donation and profile serializers do not include fraud fields. Alert detail omits pickup addresses and full nested actor/donation objects. Audit records are read-only in Django Admin.

Review outcomes are `NO_ACTION`, `FALSE_POSITIVE`, `POLICY_VIOLATION`, and `ESCALATED`. The first three resolve the alert; `ESCALATED` leaves it `REVIEWING` for another human reviewer. A resolved alert cannot be re-reviewed via the same action. Review notes should contain only operationally necessary information.

## Limitations and operational guidance

Legitimate bulk donors, event-based surges, recurring logistics failures, and contested complaints may trigger false positives. Similarity and volume heuristics are sensitive to local operating patterns, units, and calendar effects. Current activity counters are simple rolling counts; they do not establish intent. Tune thresholds only with documented review evidence, monitor false-positive rates, and retain human review before any consequential decision. Collect production labels and establish governance before considering trained fraud models.
