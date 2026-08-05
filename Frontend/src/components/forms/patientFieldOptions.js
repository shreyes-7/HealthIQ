/**
 * Human-readable option labels for the NHAMCS-coded fields the backend
 * accepts as raw integers. Confirmed against
 * `Data/documents/technical Documentation.pdf` (Sprint 5) -- not guessed.
 * The backend contract (`Backend.app.schemas.patient.PatientRecordRequest`)
 * still receives the numeric codes; this is presentation-only.
 */

export const SEX_OPTIONS = [
  { value: 1, label: 'Female' },
  { value: 2, label: 'Male' },
]

export const RACE_ETHNICITY_OPTIONS = [
  { value: 1, label: 'Non-Hispanic White' },
  { value: 2, label: 'Non-Hispanic Black' },
  { value: 3, label: 'Hispanic' },
  { value: 4, label: 'Non-Hispanic Other' },
]

export const TRIAGE_LEVEL_OPTIONS = [
  { value: 1, label: 'Immediate' },
  { value: 2, label: 'Emergent' },
  { value: 3, label: 'Urgent' },
  { value: 4, label: 'Semi-urgent' },
  { value: 5, label: 'Non-urgent' },
]
