# FoodShare AI NGO Matching Engine

## Purpose and score semantics

The matching engine ranks eligible, verified NGOs for an available food donation using a deterministic weighted score. The score is a **ranking score from 0 to 100**, not an ML output, probability, or guarantee of suitability. It is built in `backend/apps/matching/services.py`; views only handle HTTP concerns.

## Eligibility filters

An NGO is eligible only when all conditions hold:

- The user account is active and has the NGO role.
- The NGO profile is marked verified and the separate NGO verification record is approved.
- The matching profile is active.
- The matching profile explicitly accepts the donation's food category.
- Its available capacity is positive and at least the donation quantity converted to kilograms. Supported conversion units are kg, g, and lb (plus common singular/plural spellings). Unsupported units are safely excluded rather than compared as if equivalent.
- The donation is unexpired and has `AVAILABLE` status at recommendation generation time.

NGO capacity, demand, location, and accepted categories are managed in the NGO dashboard. Reliability is stored in the matching profile but intentionally read-only through the NGO API; administrators manage it.

## Factors and formula

Each factor is normalized to the 0–100 range. The six configured weights default to:

| Factor | Default weight | Scoring |
| --- | ---: | --- |
| Distance | 30% | With both coordinate pairs: `100 * (1 - min(distance_km / max_distance_km, 1))`. Haversine distance uses mean Earth radius 6371.0088 km. |
| Food compatibility | 20% | 100 when the NGO explicitly accepts the donation category; otherwise the NGO is excluded. |
| Urgency | 20% | `100 * (1 - min(remaining_hours / urgency_horizon_hours, 1))`, clamped to 0–100. |
| Capacity | 15% | `100 * (1 - donation_kg / available_capacity_kg)`, clamped to 0–100. NGOs lacking capacity are excluded. |
| Current demand | 10% | NGO-maintained integer from 0 to 100. |
| Reliability | 5% | Administrator-maintained integer from 0 to 100. |

Weights are normalized by their sum before use, allowing custom weights whose sum is not exactly one. The weighted score is:

$$\text{score} = \frac{\sum_i \text{weight}_i \times \text{factorScore}_i}{\sum_i \text{weight}_i}$$

The final result is clamped to 0–100 and rounded to two decimal places. Each factor's score and effective weight are persisted alongside a human-readable explanation.

## Missing coordinates and limits

When either the donation or NGO coordinate pair is incomplete, distance is omitted (`distance_km: null`) and receives a neutral factor score of 50/100. The explanation explicitly states that distance was unavailable. The engine does not geocode textual addresses. A neutral score avoids treating unknown locations as nearby or silently excluding them.

Urgency is based on remaining time to expiry, not a learned urgency model. The capacity comparison assumes a convertible quantity expressed in mass; unsupported units are excluded. The system does not yet model partial allocation, route travel time, service-area boundaries, stock already committed to other donations, or independently measured demand. Demand and reliability values are operational inputs and may be subjective.

Only the top `limit` results are returned (default 10, maximum 50), sorted by descending score and then NGO id. Recommendation explanations include distance, compatibility, urgency, capacity use, demand, and reliability details.

## Configuration

Django settings in `backend/config/settings/base.py` expose the weights and score horizons, all configurable with environment variables:

- `MATCHING_WEIGHT_DISTANCE` (default `0.30`)
- `MATCHING_WEIGHT_FOOD_COMPATIBILITY` (default `0.20`)
- `MATCHING_WEIGHT_URGENCY` (default `0.20`)
- `MATCHING_WEIGHT_CAPACITY` (default `0.15`)
- `MATCHING_WEIGHT_CURRENT_DEMAND` (default `0.10`)
- `MATCHING_WEIGHT_RELIABILITY` (default `0.05`)
- `MATCHING_MAX_DISTANCE_KM` (default `100`)
- `MATCHING_URGENCY_HORIZON_HOURS` (default `72`)

Weights must be non-negative with a positive total. Distance and urgency horizons must be positive. The score service normalizes weights at runtime.

## Persistence and status handling

`NGORecommendation` persists the score, per-factor values, effective weights, distance, explanation, status, and timestamps. A conditional database unique constraint allows at most one active (`RECOMMENDED` or `ACCEPTED`) recommendation per donation and NGO. Regeneration refreshes existing recommended rows, and marks no-longer-eligible recommendations `SUPERSEDED`.

Recommendation generation is transactional. Accepting a recommendation locks the recommendation and donation, verifies current eligibility and expiry, transitions the donation through the existing donation status service to `MATCHED` and `ACCEPTED`, records status history, supersedes competing recommendations, and marks the selected recommendation accepted in one transaction. Declines are scoped to the authenticated NGO.

## Endpoints

All routes require JWT authentication.

- `GET /api/matching/profile/` — get or initialize the signed-in NGO's matching profile.
- `PATCH /api/matching/profile/` — update accepted category IDs, coordinates, capacity (kg), and current demand (0–100).
- `POST /api/matching/donations/{donation_id}/generate/?limit=10` — donor-only; generate and persist ranked recommendations for a donation owned by that donor.
- `GET /api/matching/donations/{donation_id}/matches/` — donor owner sees all active recommendations; an NGO sees only its own recommendation for the donation.
- `GET /api/matching/my/` — donor sees recommendations for their donations; NGO sees their own active recommendations.
- `POST /api/matching/matches/{recommendation_id}/accept/` — accept an NGO recommendation transactionally.
- `POST /api/matching/matches/{recommendation_id}/decline/` — decline an NGO recommendation.

Generation response includes `score_type: weighted_ranking_score` to prevent confusion with ML probabilities. The donor and NGO dashboards display the score, distance when available, compatibility, factor explanations, and current status.
