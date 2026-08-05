import apiClient from './apiClient'

/**
 * patientRecord must match Backend.app.schemas.patient.PatientRecordRequest
 * exactly -- the backend rejects unknown fields.
 */
export function submitPrediction(patientRecord) {
  return apiClient.post('/api/v1/predict', patientRecord)
}
