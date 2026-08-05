/**
 * Field metadata and validation mirroring
 * Backend.app.schemas.patient.PatientRecordRequest's constraints exactly,
 * so obviously-invalid submissions never reach the network (per
 * PROJECT_CONTEXT.md §81: "Input validation should occur before requests
 * are sent to the backend").
 */

export const REQUIRED_NUMERIC_FIELDS = {
  age: { min: 0, max: 120, label: 'Age' },
  pulse: { min: 0, max: 300, label: 'Pulse' },
  temperature_fahrenheit: { min: 70, max: 115, label: 'Temperature' },
  respiratory_rate: { min: 0, max: 100, label: 'Respiratory rate' },
  systolic_bp: { min: 0, max: 300, label: 'Systolic blood pressure' },
  diastolic_bp: { min: 0, max: 200, label: 'Diastolic blood pressure' },
}

export const OPTIONAL_NUMERIC_FIELDS = {
  pulse_oximetry_percent: { min: 0, max: 100, label: 'Pulse oximetry' },
  wait_time_minutes: { min: 0, max: null, label: 'Wait time' },
  length_of_visit_minutes: { min: 0, max: null, label: 'Length of visit' },
  num_discharge_diagnoses: { min: 0, max: 20, label: 'Number of discharge diagnoses' },
  total_diagnoses: { min: 0, max: 20, label: 'Total diagnoses' },
  num_medications: { min: 0, max: 50, label: 'Number of medications' },
  num_medications_given: { min: 0, max: 50, label: 'Number of medications given' },
}

export const REQUIRED_SELECT_FIELDS = ['sex', 'triage_level']
export const REQUIRED_BOOLEAN_FIELDS = ['arrived_by_ambulance']

export const INITIAL_FORM_VALUES = {
  age: '',
  sex: '',
  race_ethnicity: '',
  pulse: '',
  temperature_fahrenheit: '',
  respiratory_rate: '',
  systolic_bp: '',
  diastolic_bp: '',
  pulse_oximetry_percent: '',
  triage_level: '',
  arrived_by_ambulance: '',
  wait_time_minutes: '',
  length_of_visit_minutes: '',
  num_discharge_diagnoses: '',
  total_diagnoses: '',
  consult_requested: '',
  primary_diagnosis_code: '',
  num_medications: '',
  num_medications_given: '',
}

function validateNumericField(rawValue, { min, max, label }, required) {
  if (rawValue === '') {
    return required ? `${label} is required.` : null
  }

  const numericValue = Number(rawValue)
  if (Number.isNaN(numericValue)) {
    return `${label} must be a number.`
  }
  if (min !== null && numericValue < min) {
    return `${label} must be at least ${min}.`
  }
  if (max !== null && numericValue > max) {
    return `${label} must be at most ${max}.`
  }
  return null
}

export function validatePatientRecordForm(values) {
  const errors = {}

  for (const [field, config] of Object.entries(REQUIRED_NUMERIC_FIELDS)) {
    const error = validateNumericField(values[field], config, true)
    if (error) errors[field] = error
  }

  for (const [field, config] of Object.entries(OPTIONAL_NUMERIC_FIELDS)) {
    const error = validateNumericField(values[field], config, false)
    if (error) errors[field] = error
  }

  for (const field of REQUIRED_SELECT_FIELDS) {
    if (values[field] === '') errors[field] = 'This field is required.'
  }

  for (const field of REQUIRED_BOOLEAN_FIELDS) {
    if (values[field] === '') errors[field] = 'This field is required.'
  }

  if (values.primary_diagnosis_code && values.primary_diagnosis_code.length > 10) {
    errors.primary_diagnosis_code = 'Diagnosis code must be at most 10 characters.'
  }

  return errors
}

const BOOLEAN_FIELDS = new Set(['arrived_by_ambulance', 'consult_requested'])
const INTEGER_FIELDS = new Set([
  'age',
  'sex',
  'race_ethnicity',
  'pulse',
  'respiratory_rate',
  'systolic_bp',
  'diastolic_bp',
  'pulse_oximetry_percent',
  'triage_level',
  'wait_time_minutes',
  'length_of_visit_minutes',
  'num_discharge_diagnoses',
  'total_diagnoses',
  'num_medications',
  'num_medications_given',
])

/**
 * Converts form state (all strings, since HTML inputs are string-valued)
 * into the shape Backend.app.schemas.patient.PatientRecordRequest expects:
 * numbers as numbers, booleans as booleans, and every field the user left
 * blank omitted entirely (not sent as null/empty-string) so the backend's
 * own imputation decides what to do with it.
 */
export function buildPatientRecordPayload(values) {
  const payload = {}

  for (const [field, rawValue] of Object.entries(values)) {
    if (rawValue === '') continue

    if (BOOLEAN_FIELDS.has(field)) {
      payload[field] = rawValue === 'true'
    } else if (INTEGER_FIELDS.has(field)) {
      payload[field] = Number(rawValue)
    } else if (field === 'temperature_fahrenheit') {
      payload[field] = Number(rawValue)
    } else {
      payload[field] = rawValue
    }
  }

  return payload
}
