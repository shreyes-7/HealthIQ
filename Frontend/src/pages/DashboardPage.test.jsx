import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import DashboardPage from './DashboardPage'
import { getDatabaseHealth, getLiveness, getModelHealth } from '../services/healthApi'
import { listPredictions } from '../services/historyApi'

vi.mock('../services/healthApi')
vi.mock('../services/historyApi')

function renderDashboard() {
  return render(
    <MemoryRouter>
      <DashboardPage />
    </MemoryRouter>,
  )
}

describe('DashboardPage', () => {
  it('shows one card as unavailable without blanking the others', async () => {
    getLiveness.mockResolvedValue({ status: 'ok' })
    getModelHealth.mockRejectedValue(new Error('model unavailable'))
    getDatabaseHealth.mockResolvedValue({ status: 'ok' })
    listPredictions.mockResolvedValue([])

    renderDashboard()

    await waitFor(() => expect(screen.getByText(/unavailable — retry/i)).toBeInTheDocument())

    // The failing "Model" row does not prevent the rest of the dashboard from rendering.
    expect(screen.getByText('Recent predictions')).toBeInTheDocument()
    expect(screen.getByText('New Prediction')).toBeInTheDocument()
  })

  it('renders an empty state when there is no prediction history yet', async () => {
    getLiveness.mockResolvedValue({ status: 'ok' })
    getModelHealth.mockResolvedValue({ model_name: 'lightgbm', model_version: '1.0.0' })
    getDatabaseHealth.mockResolvedValue({ status: 'ok' })
    listPredictions.mockResolvedValue([])

    renderDashboard()

    await waitFor(() => expect(screen.getByText('No predictions have been made yet.')).toBeInTheDocument())
  })

  it('renders recent predictions when history exists', async () => {
    getLiveness.mockResolvedValue({ status: 'ok' })
    getModelHealth.mockResolvedValue({ model_name: 'lightgbm', model_version: '1.0.0' })
    getDatabaseHealth.mockResolvedValue({ status: 'ok' })
    listPredictions.mockResolvedValue([
      {
        id: '1',
        created_at: '2026-08-04T12:00:00Z',
        risk_category: 'low',
        admission_probability: 0.12,
      },
    ])

    renderDashboard()

    await waitFor(() => expect(screen.getByText('low risk')).toBeInTheDocument())
    expect(screen.getByText('12.0%')).toBeInTheDocument()
  })
})
