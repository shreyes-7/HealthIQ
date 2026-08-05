import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import LandingPage from './pages/LandingPage'
import DashboardPage from './pages/DashboardPage'
import ScrollToTop from '@/components/ScrollToTop'
import { Skeleton } from '@/components/ui/skeleton'

// The public landing page ("/") and the app shell's own Dashboard load
// eagerly for an instant first paint. The other in-app pages -- especially
// Prediction and Explainability, which pull in Recharts -- are code-split so
// a first-time visitor's initial bundle isn't paying for charting code
// before they've asked to see a chart.
const PredictionPage = lazy(() => import('./pages/PredictionPage'))
const ExplainabilityPage = lazy(() => import('./pages/ExplainabilityPage'))
const PredictionHistoryPage = lazy(() => import('./pages/PredictionHistoryPage'))
const AboutPage = lazy(() => import('./pages/AboutPage'))

function RouteFallback() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-64 w-full" />
    </div>
  )
}

function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route
            path="predict"
            element={
              <Suspense fallback={<RouteFallback />}>
                <PredictionPage />
              </Suspense>
            }
          />
          <Route
            path="explainability"
            element={
              <Suspense fallback={<RouteFallback />}>
                <ExplainabilityPage />
              </Suspense>
            }
          />
          <Route
            path="history"
            element={
              <Suspense fallback={<RouteFallback />}>
                <PredictionHistoryPage />
              </Suspense>
            }
          />
          <Route
            path="about"
            element={
              <Suspense fallback={<RouteFallback />}>
                <AboutPage />
              </Suspense>
            }
          />
        </Route>
      </Routes>
    </>
  )
}

export default App
