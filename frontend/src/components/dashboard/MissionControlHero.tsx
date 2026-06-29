import { motion } from 'framer-motion';

export function MissionControlHero() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30, delay: 0 }}
      className="relative w-full h-[400px] bg-atmosphere-dashboard-main rounded-[12px] overflow-hidden shadow-panel border border-border flex flex-col justify-end p-8"
    >
      {/* Abstract Animated Nodes representing Pipeline */}
      <div className="absolute inset-0 z-0">
        <svg className="w-full h-full opacity-30" viewBox="0 0 1000 400" preserveAspectRatio="none">
          <motion.path
            d="M0,200 C300,200 400,100 600,150 C800,200 900,100 1000,150"
            fill="none"
            stroke="url(#glow-gradient)"
            strokeWidth="1.5"
            strokeLinecap="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, ease: "easeInOut", repeat: Infinity, repeatType: "reverse" }}
          />
          <defs>
            <linearGradient id="glow-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3B82F6" stopOpacity="0" />
              <stop offset="50%" stopColor="#3B82F6" stopOpacity="1" />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="relative z-10 flex flex-col items-start gap-2">
        <h2 className="text-editorial-hero font-sans text-atmosphere-dashboard-light font-semibold tracking-tight text-3xl">
          Mission Control
        </h2>
        <p className="text-foreground-muted font-sans max-w-lg text-sm leading-relaxed">
          Central execution topology is stable. 4 active pipelines orchestrating 127 deterministic operations.
          Zero critical alerts across primary clusters.
        </p>
        
        <div className="mt-4 flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-accent"></span>
            </span>
            <span className="text-xs font-mono text-atmosphere-dashboard-light uppercase tracking-wider">System Operational</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
