import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AboutPage from './AboutPage'
import { getModelHealth } from '../services/healthApi'

vi.mock('../services/healthApi')

beforeEach(() => {
  vi.clearAllMocks()
})

function renderAboutPage() {
  return render(
    <MemoryRouter>
      <AboutPage />
    </MemoryRouter>,
  )
}

describe('AboutPage', () => {
  it('renders the structured content sections', () => {
    getModelHealth.mockResolvedValue({ model_name: 'lightgbm', model_version: '1.0.0' })

    renderAboutPage()

    expect(screen.getByText('What it does')).toBeInTheDocument()
    expect(screen.getByText('How predictions work')).toBeInTheDocument()
    expect(screen.getByText('About the model')).toBeInTheDocument()
  })

  it('shows the live model name/version rather than hardcoded text', async () => {
    getModelHealth.mockResolvedValue({ model_name: 'lightgbm', model_version: '1.0.0' })

    renderAboutPage()

    expect(await screen.findByText('Currently serving lightgbm v1.0.0')).toBeInTheDocument()
  })

  it('discloses data provenance, storage, and model limitations', () => {
    getModelHealth.mockResolvedValue({ model_name: 'lightgbm', model_version: '1.0.0' })

    renderAboutPage()

    expect(screen.getByText('Data & privacy')).toBeInTheDocument()
    expect(screen.getByText('Limitations')).toBeInTheDocument()
  })
})
