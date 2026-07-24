# Target Variable and Survey Design Variables

Generated: 2026-07-24T15:37:34.539254+00:00

## Target Variable

NHAMCS does not provide a single binary "admitted" column. Visit disposition
is recorded as a set of independent 0/1 checkbox items (see technical
documentation, "VISIT DISPOSITION" item group, item numbers 226-241).

The two items relevant to hospital admission are:

- `ADMITHOS` - "Admit to this hospital" (0 = No, 1 = Yes)
- `OBSHOS` - "Admit to observation unit, then
  hospitalized" (0 = No, 1 = Yes)

This project defines the prediction target, `hospital_admission`,
as:

    hospital_admission = 1 if (ADMITHOS == 1 or OBSHOS == 1) else 0

Note: `ADMIT` ("Admitted to:") is a *different* variable describing which
hospital unit (critical care, stepdown, OR, etc.) a patient was admitted to.
It is only populated for visits already flagged as admitted and is not a
usable prediction target on its own.

**Empirical check (this dataset, 16,025 visits):**

| ADMITHOS | OBSHOS | Visits |
|---|---|---|
| 0 | 0 | 13,904 |
| 1 | 0 | 1,944 |
| 1 | 1 | 177 |

Every visit with `OBSHOS == 1` also has
`ADMITHOS == 1`. In this dataset `ADMITHOS`
alone already equals the full admitted population (2,121 visits); `OBSHOS`
adds route-of-admission detail, not additional coverage. The OR-based
derivation above is therefore safe and future-proof (it would still be
correct if a future data release breaks that overlap), but the practical
effect today is equivalent to using `ADMITHOS` alone.

Deriving the target column itself is a Milestone 5 (Feature Engineering)
task; this milestone only identifies and documents the source variables.

## Survey Design Variables

NHAMCS is a complex, weighted, clustered sample rather than a simple random
sample. The technical documentation (Appendix I.A and Section H) confirms
the survey design with the example:

    svyset [pweight=patwt], psu(cpsum) strata(cstratm)

| Variable | Role | Description |
|---|---|---|
| `PATWT` | Weight | Patient visit weight - required to produce national estimates |
| `CSTRATM` | Strata | Clustered PSU stratum marker (masked) |
| `CPSUM` | Cluster / PSU | Clustered PSU marker (masked) |
| `EDWT` | Facility weight | ED-level weight; used only for facility-level estimates, not patient-level prediction |

These variables must be preserved through preprocessing for the
survey-aware learning workflow (Milestone 8) and must never be used as
ordinary predictive features in the traditional ML workflow.
