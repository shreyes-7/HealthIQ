import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import PatientRecordForm from './PatientRecordForm'

async function selectOption(user, labelPattern, optionName) {
  await user.click(screen.getByLabelText(labelPattern))
  await user.click(await screen.findByRole('option', { name: optionName }))
}

async function fillRequiredFields(user) {
  await user.type(screen.getByLabelText(/Age/), '67')
  await selectOption(user, /Sex/, 'Male')
  await user.type(screen.getByLabelText(/^Pulse \(bpm\)/), '88')
  await user.type(screen.getByLabelText(/Temperature/), '98.6')
  await user.type(screen.getByLabelText(/Respiratory rate/), '18')
  await user.type(screen.getByLabelText(/Systolic BP/), '130')
  await user.type(screen.getByLabelText(/Diastolic BP/), '80')
  await selectOption(user, /Triage level/, 'Emergent')
  await selectOption(user, /Arrived by ambulance/, 'Yes')
}

describe('PatientRecordForm', () => {
  it('shows the confirmed human-readable NHAMCS labels, not raw codes', async () => {
    const user = userEvent.setup()
    render(<PatientRecordForm onSubmit={vi.fn()} />)

    await user.click(screen.getByLabelText(/Sex/))
    expect(await screen.findByRole('option', { name: 'Female' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Male' })).toBeInTheDocument()
    await user.keyboard('{Escape}')

    await user.click(screen.getByLabelText(/Triage level/))
    expect(await screen.findByRole('option', { name: 'Immediate' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Non-urgent' })).toBeInTheDocument()
    await user.keyboard('{Escape}')

    await user.click(screen.getByLabelText(/Race\/Ethnicity/))
    expect(await screen.findByRole('option', { name: 'Hispanic' })).toBeInTheDocument()
  })

  it('blocks submission and shows field errors when required fields are missing', () => {
    const onSubmit = vi.fn()
    render(<PatientRecordForm onSubmit={onSubmit} />)

    fireEvent.click(screen.getByRole('button', { name: /generate prediction/i }))

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getAllByRole('alert').length).toBeGreaterThan(0)
  })

  it('submits the correctly-typed payload once all required fields are valid', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<PatientRecordForm onSubmit={onSubmit} />)

    await fillRequiredFields(user)
    await user.click(screen.getByRole('button', { name: /generate prediction/i }))

    expect(onSubmit).toHaveBeenCalledWith({
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

  it('disables the submit button while isSubmitting is true', () => {
    render(<PatientRecordForm onSubmit={vi.fn()} isSubmitting />)

    expect(screen.getByRole('button', { name: /generating prediction/i })).toBeDisabled()
  })
})
