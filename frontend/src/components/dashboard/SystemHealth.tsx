import { motion } from 'framer-motion';

export function SystemHealth() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30, delay: 0.05 }}
      className="p-6 bg-surface rounded-[8px] border border-border shadow-panel flex flex-col gap-4"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-sans font-medium text-foreground tracking-tight">System Health</h3>
        <span className="text-2xs font-mono text-muted uppercase tracking-wider">Live</span>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mt-2">
        <div className="flex flex-col gap-1">
          <span className="text-xs text-muted font-sans">CPU Utilization</span>
          <span className="text-xl font-mono text-foreground">12.4%</span>
          <div className="w-full h-1 bg-surface-elevated rounded-full overflow-hidden">
            <div className="h-full bg-accent w-[12.4%]" />
          </div>
        </div>
        <div className="flex flex-col gap-1">
          <span className="text-xs text-muted font-sans">Memory</span>
          <span className="text-xl font-mono text-foreground">48.2%</span>
          <div className="w-full h-1 bg-surface-elevated rounded-full overflow-hidden">
            <div className="h-full bg-accent w-[48.2%]" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
