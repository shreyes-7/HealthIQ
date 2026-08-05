import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

function FieldError({ id, error }) {
  if (!error) return null
  return (
    <p id={id} role="alert" className="text-sm text-destructive">
      {error}
    </p>
  )
}

function FieldLabel({ name, label, required }) {
  return (
    <Label htmlFor={name}>
      {label}
      {required && (
        <span aria-hidden="true" className="text-destructive">
          *
        </span>
      )}
    </Label>
  )
}

export function TextField({ label, name, value, onChange, error, required = false, ...rest }) {
  const errorId = `${name}-error`

  return (
    <div className="space-y-1.5">
      <FieldLabel name={name} label={label} required={required} />
      <Input
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
        aria-required={required}
        {...rest}
      />
      <FieldError id={errorId} error={error} />
    </div>
  )
}

export function SelectField({ label, name, value, onValueChange, error, required = false, options, placeholder }) {
  const errorId = `${name}-error`

  return (
    <div className="space-y-1.5">
      <FieldLabel name={name} label={label} required={required} />
      <Select value={value || undefined} onValueChange={(next) => onValueChange(name, next)}>
        <SelectTrigger
          id={name}
          className="w-full"
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          aria-required={required}
        >
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option.value} value={String(option.value)}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <FieldError id={errorId} error={error} />
    </div>
  )
}
