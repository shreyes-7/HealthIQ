import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import LandingPage from './LandingPage'

function renderLandingPage() {
  return render(
    <MemoryRouter>
      <LandingPage />
    </MemoryRouter>,
  )
}

describe('LandingPage', () => {
  it('renders the hero heading and a primary call-to-action linking into the app', () => {
    renderLandingPage()

    expect(
      screen.getByRole('heading', { level: 1, name: /emergency department admission risk/i }),
    ).toBeInTheDocument()

    const ctaLinks = screen.getAllByRole('link', { name: /launch the app|launch app/i })
    expect(ctaLinks.length).toBeGreaterThan(0)
    ctaLinks.forEach((link) => expect(link).toHaveAttribute('href', '/app'))
  })

  it('renders the how-it-works steps and the clinical-judgment disclaimer', () => {
    renderLandingPage()

    expect(screen.getByText('Enter patient vitals & triage info')).toBeInTheDocument()
    expect(screen.getByText('Get a calibrated risk score')).toBeInTheDocument()
    expect(screen.getByText('Review the explanation')).toBeInTheDocument()
    expect(screen.getByText(/intended to support clinical judgment, not replace it/i)).toBeInTheDocument()
  })

  it('links every footer nav item into the app shell, not the marketing page', () => {
    renderLandingPage()

    expect(screen.getByRole('link', { name: 'Dashboard' })).toHaveAttribute('href', '/app')
    expect(screen.getByRole('link', { name: 'Prediction' })).toHaveAttribute('href', '/app/predict')
    expect(screen.getByRole('link', { name: 'Explainability' })).toHaveAttribute('href', '/app/explainability')
    expect(screen.getByRole('link', { name: 'Prediction History' })).toHaveAttribute('href', '/app/history')
    expect(screen.getByRole('link', { name: 'About' })).toHaveAttribute('href', '/app/about')
  })
})
