import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import PredictionHistoryPage from './PredictionHistoryPage'
import { listPredictions } from '../services/historyApi'

vi.mock('../services/historyApi')

beforeEach(() => {
  vi.clearAllMocks()
})

const SAMPLE_RECORD = {
  id: '1',
  created_at: '2026-08-04T12:00:00Z',
  predicted_admission: true,
  admission_probability: 0.82,
  risk_category: 'high',
  model_name: 'lightgbm',
  model_version: '1.0.0',
  processing_time_ms: 1234.5,
}

describe('PredictionHistoryPage', () => {
  it('loads history on mount with the default limit', async () => {
    listPredictions.mockResolvedValue([SAMPLE_RECORD])

    render(<PredictionHistoryPage />)

    await waitFor(() => expect(listPredictions).toHaveBeenCalledWith(50))
    expect(await screen.findByText('Admission')).toBeInTheDocument()
    expect(screen.getByText('82.0%')).toBeInTheDocument()
    expect(screen.getByText('high risk')).toBeInTheDocument()
    expect(screen.getByText('1235 ms')).toBeInTheDocument()
  })

  it('shows an empty state when there is no history', async () => {
    listPredictions.mockResolvedValue([])

    render(<PredictionHistoryPage />)

    expect(await screen.findByText('No predictions have been made yet.')).toBeInTheDocument()
  })

  it('re-fetches when the limit changes', async () => {
    listPredictions.mockResolvedValue([])

    render(<PredictionHistoryPage />)
    await waitFor(() => expect(listPredictions).toHaveBeenCalledWith(50))

    fireEvent.change(screen.getByLabelText(/number of records/i), { target: { value: '10' } })

    await waitFor(() => expect(listPredictions).toHaveBeenCalledWith(10))
  })

  it('shows an error state on failure', async () => {
    listPredictions.mockRejectedValue(new Error('The database is not reachable.'))

    render(<PredictionHistoryPage />)

    expect(await screen.findByText('The database is not reachable.')).toBeInTheDocument()
  })

  it('filters the currently-loaded page by risk category without a new fetch', async () => {
    listPredictions.mockResolvedValue([
      { ...SAMPLE_RECORD, id: '1', risk_category: 'high' },
      { ...SAMPLE_RECORD, id: '2', risk_category: 'low' },
    ])

    render(<PredictionHistoryPage />)
    await waitFor(() => expect(screen.getAllByText(/risk$/)).toHaveLength(2))

    fireEvent.click(screen.getByRole('radio', { name: 'Low' }))

    await waitFor(() => expect(screen.getAllByText(/risk$/)).toHaveLength(1))
    expect(screen.getByText('low risk')).toBeInTheDocument()
    expect(listPredictions).toHaveBeenCalledTimes(1) // filtering is client-side, not a re-fetch
  })

  it('sorts by clicking a column header, toggling direction on repeated clicks', async () => {
    listPredictions.mockResolvedValue([
      { ...SAMPLE_RECORD, id: '1', admission_probability: 0.2 },
      { ...SAMPLE_RECORD, id: '2', admission_probability: 0.9 },
    ])

    render(<PredictionHistoryPage />)
    await waitFor(() => expect(screen.getAllByRole('row')).toHaveLength(3)) // header + 2 rows

    const firstRowProbability = () => screen.getAllByRole('row')[1].textContent

    // Clicking a new column defaults to descending (highest first).
    fireEvent.click(screen.getByRole('button', { name: /probability/i }))
    expect(firstRowProbability()).toContain('90.0%')

    // Clicking the same column again toggles to ascending.
    fireEvent.click(screen.getByRole('button', { name: /probability/i }))
    expect(firstRowProbability()).toContain('20.0%')
  })
})
