import { motion } from 'framer-motion';

export function LiveEventFeed() {
  const events = [
    { id: 'ev-1', time: '14:23:10', msg: 'Pipeline optimization complete', status: 'success' },
    { id: 'ev-2', time: '14:22:45', msg: 'Replay #8932 synchronized', status: 'info' },
    { id: 'ev-3', time: '14:20:01', msg: 'Worker node spin-up (US-East)', status: 'info' },
    { id: 'ev-4', time: '14:18:33', msg: 'Artifact bundle signed', status: 'success' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30, delay: 0.1 }}
      className="p-6 bg-surface rounded-[8px] border border-border shadow-panel flex flex-col gap-4 h-full"
    >
      <div className="flex items-center justify-between border-b border-border pb-4">
        <h3 className="text-lg font-sans font-medium text-foreground tracking-tight">Live Event Feed</h3>
      </div>
      
      <div className="flex flex-col gap-3 mt-2 overflow-y-auto">
        {events.map((ev, i) => (
          <motion.div 
            key={ev.id}
            initial={{ opacity: 0, x: -5 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 + (i * 0.05) }}
            className="flex items-start gap-3 p-2 hover:bg-surface-elevated rounded-md transition-colors group cursor-default"
          >
            <span className="text-xs font-mono text-muted whitespace-nowrap mt-0.5">{ev.time}</span>
            <div className="flex flex-col">
              <span className="text-sm font-sans text-foreground group-hover:text-accent transition-colors">{ev.msg}</span>
              <span className="text-xs font-mono text-muted uppercase mt-0.5">{ev.status}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
