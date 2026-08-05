import { describe, expect, it } from 'vitest'
import { INITIAL_FORM_VALUES, buildPatientRecordPayload, validatePatientRecordForm } from './patientRecordFormConfig'

const VALID_VALUES = {
  ...INITIAL_FORM_VALUES,
  age: '67',
  sex: '2',
  pulse: '88',
  temperature_fahrenheit: '98.6',
  respiratory_rate: '18',
  systolic_bp: '130',
  diastolic_bp: '80',
  triage_level: '2',
  arrived_by_ambulance: 'true',
}

describe('validatePatientRecordForm', () => {
  it('returns no errors for a fully valid, minimal (required-only) submission', () => {
    expect(validatePatientRecordForm(VALID_VALUES)).toEqual({})
  })

  it('flags every missing required field', () => {
    const errors = validatePatientRecordForm(INITIAL_FORM_VALUES)

    expect(errors).toHaveProperty('age')
    expect(errors).toHaveProperty('sex')
    expect(errors).toHaveProperty('pulse')
    expect(errors).toHaveProperty('temperature_fahrenheit')
    expect(errors).toHaveProperty('respiratory_rate')
    expect(errors).toHaveProperty('systolic_bp')
    expect(errors).toHaveProperty('diastolic_bp')
    expect(errors).toHaveProperty('triage_level')
    expect(errors).toHaveProperty('arrived_by_ambulance')
  })

  it('does not require optional fields', () => {
    const errors = validatePatientRecordForm(VALID_VALUES)

    expect(errors).not.toHaveProperty('race_ethnicity')
    expect(errors).not.toHaveProperty('pulse_oximetry_percent')
    expect(errors).not.toHaveProperty('consult_requested')
  })

  it.each([
    ['age', '-1'],
    ['age', '200'],
    ['pulse', '-5'],
    ['temperature_fahrenheit', '200'],
    ['respiratory_rate', '-1'],
    ['systolic_bp', '400'],
    ['diastolic_bp', '-1'],
  ])('rejects an out-of-range %s value', (field, badValue) => {
    const errors = validatePatientRecordForm({ ...VALID_VALUES, [field]: badValue })

    expect(errors).toHaveProperty(field)
  })

  it('rejects an out-of-range optional field only when provided', () => {
    expect(validatePatientRecordForm({ ...VALID_VALUES, pulse_oximetry_percent: '150' })).toHaveProperty(
      'pulse_oximetry_percent',
    )
    expect(validatePatientRecordForm({ ...VALID_VALUES, pulse_oximetry_percent: '' })).not.toHaveProperty(
      'pulse_oximetry_percent',
    )
  })

  it('rejects a primary diagnosis code longer than 10 characters', () => {
    const errors = validatePatientRecordForm({ ...VALID_VALUES, primary_diagnosis_code: 'THISISWAYTOOLONG' })

    expect(errors).toHaveProperty('primary_diagnosis_code')
  })
})

describe('buildPatientRecordPayload', () => {
  it('omits every field the user left blank', () => {
    const payload = buildPatientRecordPayload(VALID_VALUES)

    expect(payload).not.toHaveProperty('race_ethnicity')
    expect(payload).not.toHaveProperty('consult_requested')
    expect(payload).not.toHaveProperty('primary_diagnosis_code')
  })

  it('converts numeric fields to numbers and booleans to booleans', () => {
    const payload = buildPatientRecordPayload(VALID_VALUES)

    expect(payload).toEqual({
      age: 67,
      sex: 2,
      pulse: 88,
      temperature_fahrenheit: 98.6,
      respiratory_rate: 18,
      systolic_bp: 130,
      diastolic_bp: 80,
      triage_level: 2,
      arrived_by_ambulance: true,
    })
  })

  it('includes optional fields when provided, correctly typed', () => {
    const payload = buildPatientRecordPayload({
      ...VALID_VALUES,
      race_ethnicity: '3',
      consult_requested: 'false',
      primary_diagnosis_code: 'R079',
      num_medications: '2',
    })

    expect(payload.race_ethnicity).toBe(3)
    expect(payload.consult_requested).toBe(false)
    expect(payload.primary_diagnosis_code).toBe('R079')
    expect(payload.num_medications).toBe(2)
  })
})
