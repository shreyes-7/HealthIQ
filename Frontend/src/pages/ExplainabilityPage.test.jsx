import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import ExplainabilityPage from './ExplainabilityPage'
import { getGlobalExplanation } from '../services/explainApi'

vi.mock('../services/explainApi')

describe('ExplainabilityPage', () => {
  it('loads global explanation data on mount with the default top_n', async () => {
    getGlobalExplanation.mockResolvedValue({
      top_features: { CONSULT__Yes: 1.2 },
      top_source_variables: { CONSULT: 1.2 },
      computed_on: 'validation_split',
      n_rows: 2404,
    })

    render(<ExplainabilityPage />)

    await waitFor(() => expect(getGlobalExplanation).toHaveBeenCalledWith(20))
    expect(await screen.findByText('By encoded feature')).toBeInTheDocument()
    expect(screen.getByText('By source variable')).toBeInTheDocument()
  })

  it('re-fetches when a preset is selected', async () => {
    getGlobalExplanation.mockResolvedValue({ top_features: {}, top_source_variables: {} })

    render(<ExplainabilityPage />)
    await waitFor(() => expect(getGlobalExplanation).toHaveBeenCalledWith(20))

    fireEvent.click(screen.getByRole('radio', { name: 'Top 5' }))

    await waitFor(() => expect(getGlobalExplanation).toHaveBeenCalledWith(5))
  })

  it('re-fetches when a custom value is entered', async () => {
    getGlobalExplanation.mockResolvedValue({ top_features: {}, top_source_variables: {} })

    render(<ExplainabilityPage />)
    await waitFor(() => expect(getGlobalExplanation).toHaveBeenCalledWith(20))

    fireEvent.change(screen.getByLabelText('Custom'), { target: { value: '42' } })

    await waitFor(() => expect(getGlobalExplanation).toHaveBeenCalledWith(42))
  })

  it('shows an error state with retry when the request fails', async () => {
    getGlobalExplanation.mockRejectedValue(new Error('The model is not currently available.'))

    render(<ExplainabilityPage />)

    expect(await screen.findByText('The model is not currently available.')).toBeInTheDocument()
  })
})
