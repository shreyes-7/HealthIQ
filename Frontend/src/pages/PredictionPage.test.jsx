import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import PredictionPage from './PredictionPage'
import { submitPrediction } from '../services/predictionApi'
import { ApiError } from '../services/apiClient'

vi.mock('../services/predictionApi')

async function selectOption(user, labelPattern, optionName) {
  await user.click(screen.getByLabelText(labelPattern))
  await user.click(await screen.findByRole('option', { name: optionName }))
}

async function fillAndSubmit(user) {
  await user.type(screen.getByLabelText(/Age/), '67')
  await selectOption(user, /Sex/, 'Male')
  await user.type(screen.getByLabelText(/^Pulse \(bpm\)/), '88')
  await user.type(screen.getByLabelText(/Temperature/), '98.6')
  await user.type(screen.getByLabelText(/Respiratory rate/), '18')
  await user.type(screen.getByLabelText(/Systolic BP/), '130')
  await user.type(screen.getByLabelText(/Diastolic BP/), '80')
  await selectOption(user, /Triage level/, 'Emergent')
  await selectOption(user, /Arrived by ambulance/, 'Yes')
  await user.click(screen.getByRole('button', { name: /generate prediction/i }))
}

const SAMPLE_PREDICTION = {
  predicted_admission: false,
  admission_probability: 0.12,
  confidence_score: 0.76,
  base_rate_probability: 0.15,
  risk_category: 'low',
  features_that_increased_risk: [
    { feature: 'CONSULT__Yes', source_variable: 'CONSULT', feature_value: 1.0, shap_value: 2.1 },
  ],
  features_that_decreased_risk: [
    { feature: 'AGE', source_variable: 'AGE', feature_value: -0.5, shap_value: -0.9 },
  ],
  model_name: 'lightgbm',
  model_version: '1.0.0',
  processing_time_ms: 1234.5,
}

describe('PredictionPage', () => {
  it('displays the prediction result on success', async () => {
    const user = userEvent.setup()
    submitPrediction.mockResolvedValue(SAMPLE_PREDICTION)

    render(<PredictionPage />)
    await fillAndSubmit(user)

    await waitFor(() => expect(screen.getByText('low risk')).toBeInTheDocument())
    expect(screen.getByText('Predicted: No admission')).toBeInTheDocument()
    expect(screen.getByText('12.0%')).toBeInTheDocument()
    expect(screen.getByText('lightgbm v1.0.0')).toBeInTheDocument()
    expect(
      screen.getByText('CONSULT increased the predicted admission risk the most, while AGE decreased it the most.'),
    ).toBeInTheDocument()
  })

  it('displays a clear error message on failure without exposing internals', async () => {
    const user = userEvent.setup()
    submitPrediction.mockRejectedValue(new ApiError('Failed to generate a prediction for the given patient record.'))

    render(<PredictionPage />)
    await fillAndSubmit(user)

    await waitFor(() =>
      expect(screen.getByText('Failed to generate a prediction for the given patient record.')).toBeInTheDocument(),
    )
  })
})
