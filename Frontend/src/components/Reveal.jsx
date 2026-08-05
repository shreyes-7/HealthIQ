import { useEffect, useRef, useState } from 'react'

function prefersReducedMotion() {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Fades/slides content in the first time it scrolls into view, once, via
 * IntersectionObserver. Under prefers-reduced-motion the content renders
 * fully visible immediately instead -- there is no reduced-motion variant of
 * a scroll-reveal that still conveys the effect, so the animation is skipped
 * entirely rather than just shortened.
 */
export default function Reveal({ children, className = '', delay = 0, as: Component = 'div' }) {
  const reduceMotion = prefersReducedMotion()
  const ref = useRef(null)
  const [visible, setVisible] = useState(reduceMotion)

  useEffect(() => {
    if (reduceMotion) return undefined
    const node = ref.current
    if (!node) return undefined

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          observer.disconnect()
        }
      },
      { threshold: 0.15 },
    )
    observer.observe(node)
    return () => observer.disconnect()
    // Reduced-motion preference is read once at mount; the observer itself
    // never needs to re-run.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (reduceMotion) {
    return <Component className={className}>{children}</Component>
  }

  return (
    <Component
      ref={ref}
      className={`${visible ? 'animate-in fade-in slide-in-from-bottom-2 duration-700' : 'opacity-0'} ${className}`}
      style={delay ? { animationDelay: `${delay}ms` } : undefined}
    >
      {children}
    </Component>
  )
}
