import React from 'react'

export function ProbabilityGauge({ value = 0, size = 140, strokeWidth = 10 }) {
  const percentage = Math.min(Math.max(value * 100, 0), 100)
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  let colorClass = 'text-emerald-500 dark:text-emerald-400'
  let bgGlow = 'rgba(16, 185, 129, 0.15)'
  if (value >= 0.7) {
    colorClass = 'text-rose-500 dark:text-rose-400'
    bgGlow = 'rgba(244, 63, 94, 0.15)'
  } else if (value >= 0.35) {
    colorClass = 'text-amber-500 dark:text-amber-400'
    bgGlow = 'rgba(245, 158, 11, 0.15)'
  }

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      {/* Background radial ambient glow */}
      <div
        className="absolute inset-0 rounded-full blur-xl opacity-60 transition-all duration-700"
        style={{ backgroundColor: bgGlow }}
      />

      <svg width={size} height={size} className="rotate-[-90deg] transform">
        {/* Background Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-200 dark:text-slate-800"
          fill="transparent"
        />
        {/* Animated Progress Ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className={`${colorClass} transition-all duration-1000 ease-out`}
          fill="transparent"
        />
      </svg>
      {/* Inner Label */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold tracking-tight text-foreground">
          {percentage.toFixed(1)}%
        </span>
        <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
          Probability
        </span>
      </div>
    </div>
  )
}
