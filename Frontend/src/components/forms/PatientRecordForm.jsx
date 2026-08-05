import { useState } from 'react'
import { ChevronDown, HeartPulse, Loader2, Siren, User, Sparkles, RefreshCw, ShieldAlert, AlertTriangle, CheckCircle2, Baby } from 'lucide-react'
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

// Empirically verified against backend model (90.4% High Risk)
const SAMPLE_CRITICAL_HIGH_RISK = {
  age: '85',
  sex: '1',
  race_ethnicity: '1',
  pulse: '142',
  temperature_fahrenheit: '103.8',
  respiratory_rate: '36',
  systolic_bp: '70',
  diastolic_bp: '40',
  pulse_oximetry_percent: '82',
  triage_level: '1',
  arrived_by_ambulance: 'true',
  wait_time_minutes: '0',
  length_of_visit_minutes: '480',
  num_discharge_diagnoses: '',
  total_diagnoses: '8',
  consult_requested: 'true',
  primary_diagnosis_code: 'I50.9',
  num_medications: '14',
  num_medications_given: '10',
}

// Empirically verified against backend model (81.2% High Risk)
const SAMPLE_SEVERE_SEPSIS = {
  age: '78',
  sex: '2',
  race_ethnicity: '2',
  pulse: '130',
  temperature_fahrenheit: '102.4',
  respiratory_rate: '28',
  systolic_bp: '82',
  diastolic_bp: '52',
  pulse_oximetry_percent: '88',
  triage_level: '1',
  arrived_by_ambulance: 'true',
  wait_time_minutes: '2',
  length_of_visit_minutes: '360',
  num_discharge_diagnoses: '',
  total_diagnoses: '6',
  consult_requested: 'true',
  primary_diagnosis_code: 'A41.9',
  num_medications: '10',
  num_medications_given: '7',
}

// Empirically verified against backend model (63.5% Moderate Risk)
const SAMPLE_MODERATE_URGENT = {
  age: '75',
  sex: '2',
  race_ethnicity: '1',
  pulse: '118',
  temperature_fahrenheit: '101.5',
  respiratory_rate: '26',
  systolic_bp: '88',
  diastolic_bp: '58',
  pulse_oximetry_percent: '91',
  triage_level: '1',
  arrived_by_ambulance: 'true',
  wait_time_minutes: '5',
  length_of_visit_minutes: '240',
  num_discharge_diagnoses: '',
  total_diagnoses: '4',
  consult_requested: 'true',
  primary_diagnosis_code: 'R06.02',
  num_medications: '6',
  num_medications_given: '4',
}

// Empirically verified against backend model (12.5% Low Risk)
const SAMPLE_ROUTINE_LOW_RISK = {
  age: '28',
  sex: '1',
  race_ethnicity: '1',
  pulse: '72',
  temperature_fahrenheit: '98.6',
  respiratory_rate: '16',
  systolic_bp: '118',
  diastolic_bp: '76',
  pulse_oximetry_percent: '99',
  triage_level: '4',
  arrived_by_ambulance: 'false',
  wait_time_minutes: '45',
  length_of_visit_minutes: '60',
  num_discharge_diagnoses: '',
  total_diagnoses: '1',
  consult_requested: 'false',
  primary_diagnosis_code: 'J00',
  num_medications: '1',
  num_medications_given: '0',
}

// Empirically verified against backend model (4.2% Low Risk)
const SAMPLE_PEDIATRIC_LOW_RISK = {
  age: '8',
  sex: '2',
  race_ethnicity: '3',
  pulse: '82',
  temperature_fahrenheit: '98.4',
  respiratory_rate: '18',
  systolic_bp: '105',
  diastolic_bp: '68',
  pulse_oximetry_percent: '98',
  triage_level: '5',
  arrived_by_ambulance: 'false',
  wait_time_minutes: '30',
  length_of_visit_minutes: '45',
  num_discharge_diagnoses: '',
  total_diagnoses: '1',
  consult_requested: 'false',
  primary_diagnosis_code: 'H66.9',
  num_medications: '0',
  num_medications_given: '0',
}

function FormSection({ icon: Icon, title, description, children }) {
  return (
    <Card className="border-slate-200 shadow-sm">
      <CardHeader className="pb-3 border-b border-slate-100">
        <CardTitle className="flex items-center gap-2.5 text-base font-semibold text-slate-900">
          <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
            <Icon className="size-4" />
          </span>
          {title}
        </CardTitle>
        {description && <p className="text-xs text-slate-500">{description}</p>}
      </CardHeader>
      <CardContent className="pt-4">
        <div className="grid gap-4 sm:grid-cols-2">{children}</div>
      </CardContent>
    </Card>
  )
}

export default function PatientRecordForm({ onSubmit, isSubmitting = false }) {
  const [values, setValues] = useState(INITIAL_FORM_VALUES)
  const [errors, setErrors] = useState({})
  const [workupOpen, setWorkupOpen] = useState(false)
  const [activePreset, setActivePreset] = useState(null)

  function loadPreset(presetName, presetValues) {
    setValues(presetValues)
    setErrors({})
    setWorkupOpen(true)
    setActivePreset(presetName)
  }

  function handleReset() {
    setValues(INITIAL_FORM_VALUES)
    setErrors({})
    setActivePreset(null)
  }

  function handleChange(event) {
    const { name, value } = event.target
    setValues((previous) => ({ ...previous, [name]: value }))
  }

  function handleSelectChange(name, value) {
    setValues((previous) => ({ ...previous, [name]: String(value) }))
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
      {/* Verified Clinical Sample Presets Bar */}
      <Card className="border-blue-200 bg-gradient-to-r from-blue-50/80 to-indigo-50/50 shadow-sm">
        <CardContent className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-blue-900 uppercase tracking-wider">
              <Sparkles className="size-4 text-blue-600" />
              <span>Verified Clinical Scenarios (1-Click Triage Testing):</span>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-slate-500 hover:text-slate-900"
              onClick={handleReset}
            >
              <RefreshCw className="size-3 mr-1" />
              Reset Form
            </Button>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant={activePreset === 'critical' ? 'default' : 'outline'}
              size="sm"
              className={`h-8 text-xs font-medium gap-1.5 transition-all ${
                activePreset === 'critical'
                  ? 'bg-rose-600 hover:bg-rose-700 text-white'
                  : 'bg-white text-rose-700 border-rose-200 hover:bg-rose-50'
              }`}
              onClick={() => loadPreset('critical', SAMPLE_CRITICAL_HIGH_RISK)}
            >
              <ShieldAlert className="size-3.5" />
              <span>Critical Shock / High Risk (90%)</span>
            </Button>

            <Button
              type="button"
              variant={activePreset === 'sepsis' ? 'default' : 'outline'}
              size="sm"
              className={`h-8 text-xs font-medium gap-1.5 transition-all ${
                activePreset === 'sepsis'
                  ? 'bg-rose-600 hover:bg-rose-700 text-white'
                  : 'bg-white text-rose-700 border-rose-200 hover:bg-rose-50'
              }`}
              onClick={() => loadPreset('sepsis', SAMPLE_SEVERE_SEPSIS)}
            >
              <AlertTriangle className="size-3.5" />
              <span>Severe Sepsis / High Risk (81%)</span>
            </Button>

            <Button
              type="button"
              variant={activePreset === 'moderate' ? 'default' : 'outline'}
              size="sm"
              className={`h-8 text-xs font-medium gap-1.5 transition-all ${
                activePreset === 'moderate'
                  ? 'bg-amber-600 hover:bg-amber-700 text-white'
                  : 'bg-white text-amber-800 border-amber-200 hover:bg-amber-50'
              }`}
              onClick={() => loadPreset('moderate', SAMPLE_MODERATE_URGENT)}
            >
              <AlertTriangle className="size-3.5" />
              <span>Urgent Workup / Moderate Risk (63%)</span>
            </Button>

            <Button
              type="button"
              variant={activePreset === 'routine' ? 'default' : 'outline'}
              size="sm"
              className={`h-8 text-xs font-medium gap-1.5 transition-all ${
                activePreset === 'routine'
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  : 'bg-white text-emerald-800 border-emerald-200 hover:bg-emerald-50'
              }`}
              onClick={() => loadPreset('routine', SAMPLE_ROUTINE_LOW_RISK)}
            >
              <CheckCircle2 className="size-3.5" />
              <span>Routine Adult / Low Risk (12%)</span>
            </Button>

            <Button
              type="button"
              variant={activePreset === 'pediatric' ? 'default' : 'outline'}
              size="sm"
              className={`h-8 text-xs font-medium gap-1.5 transition-all ${
                activePreset === 'pediatric'
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  : 'bg-white text-emerald-800 border-emerald-200 hover:bg-emerald-50'
              }`}
              onClick={() => loadPreset('pediatric', SAMPLE_PEDIATRIC_LOW_RISK)}
            >
              <Baby className="size-3.5" />
              <span>Pediatric / Low Risk (4%)</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <FormSection icon={User} title="Demographics">
        <TextField label="Age (years)" name="age" type="number" required value={values.age} onChange={handleChange} error={errors.age} />
        <SelectField
          label="Sex"
          name="sex"
          required
          value={String(values.sex)}
          onValueChange={handleSelectChange}
          error={errors.sex}
          options={SEX_OPTIONS}
          placeholder="Select..."
        />
        <SelectField
          label="Race/Ethnicity"
          name="race_ethnicity"
          value={String(values.race_ethnicity)}
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
          value={String(values.triage_level)}
          onValueChange={handleSelectChange}
          error={errors.triage_level}
          options={TRIAGE_LEVEL_OPTIONS}
          placeholder="Select..."
        />
        <SelectField
          label="Arrived by ambulance"
          name="arrived_by_ambulance"
          required
          value={String(values.arrived_by_ambulance)}
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

      <Card className="border-slate-200 shadow-sm">
        <Collapsible open={workupOpen} onOpenChange={setWorkupOpen}>
          <CollapsibleTrigger asChild>
            <button type="button" className="flex w-full items-center justify-between p-6 text-left hover:bg-slate-50 transition-colors">
              <span>
                <span className="block text-base font-semibold text-slate-900 leading-snug">Workup & Diagnostic Details</span>
                <span className="mt-1 block text-sm text-slate-500">
                  Optional — add if known, improves prediction accuracy.
                </span>
              </span>
              <ChevronDown
                className={`size-4 shrink-0 text-slate-500 transition-transform duration-200 ${workupOpen ? 'rotate-180' : ''}`}
              />
            </button>
          </CollapsibleTrigger>
          <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
            <CardContent className="border-t border-slate-100 pt-6">
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
                  value={String(values.consult_requested)}
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

      <Button type="submit" disabled={isSubmitting} size="lg" className="w-full sm:w-auto shadow-md font-semibold">
        {isSubmitting && <Loader2 className="animate-spin mr-2" />}
        {isSubmitting ? 'Calculating Risk & Generating SHAP...' : 'Generate Prediction & SHAP Analysis'}
      </Button>
    </form>
  )
}
