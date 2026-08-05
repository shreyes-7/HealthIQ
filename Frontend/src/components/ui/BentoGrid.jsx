import React from 'react'

export function BentoGrid({ children, className = '' }) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 ${className}`}>
      {children}
    </div>
  )
}

export function BentoCard({
  title,
  description,
  header,
  icon: Icon,
  className = '',
  badge,
  children,
}) {
  return (
    <div
      className={`group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-border/80 bg-card p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:shadow-xl dark:bg-card/60 dark:backdrop-blur-sm ${className}`}
    >
      {/* Subtle top gradient glow on hover */}
      <div className="pointer-events-none absolute -top-24 -right-24 size-48 rounded-full bg-primary/10 blur-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

      {header && <div className="mb-4 overflow-hidden rounded-xl">{header}</div>}

      <div className="relative z-10 space-y-3">
        <div className="flex items-center justify-between">
          {Icon && (
            <div className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
              <Icon className="size-5" />
            </div>
          )}
          {badge && (
            <span className="rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium text-secondary-foreground border border-border">
              {badge}
            </span>
          )}
        </div>

        <h3 className="text-lg font-semibold tracking-tight text-foreground group-hover:text-primary transition-colors">
          {title}
        </h3>
        <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
        {children}
      </div>
    </div>
  )
}
