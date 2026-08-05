import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// With `globals: false` (vite.config.js), React Testing Library's automatic
// afterEach cleanup can't hook into Vitest's global afterEach -- without
// this, unmounted components from a previous test stay in the DOM and
// later tests see duplicate elements.
afterEach(() => {
  cleanup()
})

// jsdom doesn't implement these, but Radix UI's pointer-based components
// (Select, Dialog, etc.) call them unconditionally. Without these stubs,
// interacting with a Radix Select in a test throws
// "target.hasPointerCapture is not a function".
if (typeof Element !== 'undefined') {
  Element.prototype.hasPointerCapture ??= () => false
  Element.prototype.setPointerCapture ??= () => {}
  Element.prototype.releasePointerCapture ??= () => {}
  Element.prototype.scrollIntoView ??= () => {}
}

// jsdom doesn't implement matchMedia. Components that check
// prefers-reduced-motion/prefers-color-scheme (e.g. Reveal) call it
// unconditionally; without this stub they throw in every test that renders
// them. Always reports "no match" -- tests exercise the default (motion
// allowed) behavior.
if (typeof window !== 'undefined') {
  window.matchMedia ??= () => ({
    matches: false,
    media: '',
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })
}

// jsdom doesn't implement IntersectionObserver. Scroll-reveal components
// (e.g. Reveal) construct one on mount; without this stub they throw in
// every test that renders them. Never fires -- tests exercise the
// non-intersecting (not-yet-revealed) state, which is fine since none of
// the assertions depend on the reveal animation itself.
if (typeof window !== 'undefined') {
  window.IntersectionObserver ??= class {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
}
