import { CircleAlert } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export default function ErrorState({ error, onRetry }) {
  const message = error?.message || 'Something went wrong. Please try again.'

  return (
    <Alert variant="destructive" className="px-4 py-3">
      <CircleAlert />
      <AlertTitle>{message}</AlertTitle>
      {(error?.errors?.length > 0 || onRetry) && (
        <AlertDescription className="text-destructive/90">
          {error?.errors?.length > 0 && (
            <ul className="list-disc space-y-0.5 pl-5">
              {error.errors.map((detail, index) => (
                <li key={detail.field ?? index}>
                  {detail.field ? `${detail.field}: ` : ''}
                  {detail.message}
                </li>
              ))}
            </ul>
          )}
          {onRetry && (
            <Button type="button" variant="link" onClick={onRetry} className="h-auto p-0 text-sm text-destructive">
              Try again
            </Button>
          )}
        </AlertDescription>
      )}
    </Alert>
  )
}
