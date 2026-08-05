import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

// Client-side route changes don't reset scroll position the way a full page
// load does. Without this, navigating away from a point scrolled deep into a
// long page (e.g. a link near the bottom of the landing page) lands the next
// page already scrolled down instead of at the top.
export default function ScrollToTop() {
  const { pathname } = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])

  return null
}
