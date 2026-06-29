import { useEffect, useRef } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'

interface AnimatedCounterProps {
  value: number
  decimals?: number
  suffix?: string
  prefix?: string
  className?: string
}

export function AnimatedCounter({
  value,
  decimals = 0,
  suffix = '',
  prefix = '',
  className,
}: AnimatedCounterProps) {
  const spring = useSpring(0, { stiffness: 100, damping: 30 })
  const display = useTransform(spring, (v) =>
    `${prefix}${v.toFixed(decimals)}${suffix}`,
  )
  const ref = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    spring.set(value)
  }, [value, spring])

  useEffect(() => {
    return display.on('change', (v) => {
      if (ref.current) ref.current.textContent = v
    })
  }, [display])

  return (
    <motion.span ref={ref} className={className}>
      {prefix}
      {value.toFixed(decimals)}
      {suffix}
    </motion.span>
  )
}
