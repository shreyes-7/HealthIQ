import { useState } from 'react'
import { ChevronDown, HeartPulse, Loader2, Siren, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { SelectField, TextField } from './FormField'
import { RACE_ETHNICITY_OPTIONS, SEX_OPTIONS, TRIAGE_LEVEL_OPTIONS } from './patientFieldOptions'
import { INITIAL_FORM_VALUES, buildPatientRecordPayload, validatePatientRecordForm } from './patientRecordFormConfig'

const YES_NO_OPTIONS = [
  { value: 'true', label: 'Yes' },
  { value: 'false', label: 'No' },
]

function FormSection({ icon: Icon, title, description, children }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2.5 text-base">
          <span className="flex size-7 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Icon className="size-4" />
          </span>
          {title}
        </CardTitle>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2">{children}</div>
      </CardContent>
    </Card>
  )
}

export default function PatientRecordForm({ onSubmit, isSubmitting = false }) {
  const [values, setValues] = useState(INITIAL_FORM_VALUES)
  const [errors, setErrors] = useState({})
  const [workupOpen, setWorkupOpen] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target
    setValues((previous) => ({ ...previous, [name]: value }))
  }

  function handleSelectChange(name, value) {
    setValues((previous) => ({ ...previous, [name]: value }))
  }

  function handleSubmit(event) {
    event.preventDefault()

    const validationErrors = validatePatientRecordForm(values)
    setErrors(validationErrors)

    if (Object.keys(validationErrors).length > 0) return

    onSubmit(buildPatientRecordPayload(values))
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-6">
      <FormSection icon={User} title="Demographics">
        <TextField label="Age (years)" name="age" type="number" required value={values.age} onChange={handleChange} error={errors.age} />
        <SelectField
          label="Sex"
          name="sex"
          required
          value={values.sex}
          onValueChange={handleSelectChange}
          error={errors.sex}
          options={SEX_OPTIONS}
          placeholder="Select..."
        />
        <SelectField
          label="Race/Ethnicity"
          name="race_ethnicity"
          value={values.race_ethnicity}
          onValueChange={handleSelectChange}
          error={errors.race_ethnicity}
          options={RACE_ETHNICITY_OPTIONS}
          placeholder="Not specified"
        />
      </FormSection>

      <FormSection icon={HeartPulse} title="Vitals">
        <TextField label="Pulse (bpm)" name="pulse" type="number" required value={values.pulse} onChange={handleChange} error={errors.pulse} />
        <TextField
          label="Temperature (°F)"
          name="temperature_fahrenheit"
          type="number"
          step="0.1"
          required
          value={values.temperature_fahrenheit}
          onChange={handleChange}
          error={errors.temperature_fahrenheit}
        />
        <TextField
          label="Respiratory rate (breaths/min)"
          name="respiratory_rate"
          type="number"
          required
          value={values.respiratory_rate}
          onChange={handleChange}
          error={errors.respiratory_rate}
        />
        <TextField
          label="Systolic BP (mmHg)"
          name="systolic_bp"
          type="number"
          required
          value={values.systolic_bp}
          onChange={handleChange}
          error={errors.systolic_bp}
        />
        <TextField
          label="Diastolic BP (mmHg)"
          name="diastolic_bp"
          type="number"
          required
          value={values.diastolic_bp}
          onChange={handleChange}
          error={errors.diastolic_bp}
        />
        <TextField
          label="Pulse oximetry (%)"
          name="pulse_oximetry_percent"
          type="number"
          value={values.pulse_oximetry_percent}
          onChange={handleChange}
          error={errors.pulse_oximetry_percent}
        />
      </FormSection>

      <FormSection icon={Siren} title="Triage & Arrival">
        <SelectField
          label="Triage level"
          name="triage_level"
          required
          value={values.triage_level}
          onValueChange={handleSelectChange}
          error={errors.triage_level}
          options={TRIAGE_LEVEL_OPTIONS}
          placeholder="Select..."
        />
        <SelectField
          label="Arrived by ambulance"
          name="arrived_by_ambulance"
          required
          value={values.arrived_by_ambulance}
          onValueChange={handleSelectChange}
          error={errors.arrived_by_ambulance}
          options={YES_NO_OPTIONS}
          placeholder="Select..."
        />
        <TextField
          label="Wait time (minutes)"
          name="wait_time_minutes"
          type="number"
          value={values.wait_time_minutes}
          onChange={handleChange}
          error={errors.wait_time_minutes}
        />
        <TextField
          label="Length of visit (minutes)"
          name="length_of_visit_minutes"
          type="number"
          value={values.length_of_visit_minutes}
          onChange={handleChange}
          error={errors.length_of_visit_minutes}
        />
      </FormSection>

      <Card>
        <Collapsible open={workupOpen} onOpenChange={setWorkupOpen}>
          <CollapsibleTrigger asChild>
            <button type="button" className="flex w-full items-center justify-between p-6 text-left">
              <span>
                <span className="block text-base font-medium leading-snug">Workup details</span>
                <span className="mt-1 block text-sm text-muted-foreground">
                  Optional — add if known, improves prediction accuracy.
                </span>
              </span>
              <ChevronDown
                className={`size-4 shrink-0 text-muted-foreground transition-transform duration-200 ${workupOpen ? 'rotate-180' : ''}`}
              />
            </button>
          </CollapsibleTrigger>
          <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
            <CardContent className="border-t pt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <TextField
                  label="Number of discharge diagnoses"
                  name="num_discharge_diagnoses"
                  type="number"
                  value={values.num_discharge_diagnoses}
                  onChange={handleChange}
                  error={errors.num_discharge_diagnoses}
                />
                <TextField
                  label="Total diagnoses"
                  name="total_diagnoses"
                  type="number"
                  value={values.total_diagnoses}
                  onChange={handleChange}
                  error={errors.total_diagnoses}
                />
                <SelectField
                  label="Consult requested"
                  name="consult_requested"
                  value={values.consult_requested}
                  onValueChange={handleSelectChange}
                  error={errors.consult_requested}
                  options={YES_NO_OPTIONS}
                  placeholder="Not specified"
                />
                <TextField
                  label="Primary diagnosis code"
                  name="primary_diagnosis_code"
                  maxLength={10}
                  value={values.primary_diagnosis_code}
                  onChange={handleChange}
                  error={errors.primary_diagnosis_code}
                />
                <TextField
                  label="Number of medications"
                  name="num_medications"
                  type="number"
                  value={values.num_medications}
                  onChange={handleChange}
                  error={errors.num_medications}
                />
                <TextField
                  label="Number of medications given"
                  name="num_medications_given"
                  type="number"
                  value={values.num_medications_given}
                  onChange={handleChange}
                  error={errors.num_medications_given}
                />
              </div>
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </Card>

      <Button type="submit" disabled={isSubmitting} size="lg" className="w-full sm:w-auto">
        {isSubmitting && <Loader2 className="animate-spin" />}
        {isSubmitting ? 'Generating prediction...' : 'Generate prediction'}
      </Button>
    </form>
  )
}
