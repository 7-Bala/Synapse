import { useState, useEffect } from 'react';
import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { Surface } from '@/design-system/primitives/Surface';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import {
  Activity, Server, Database, TrendingUp, Cpu, Layers
} from 'lucide-react';

interface TelemetryMetric {
  label: string;
  value: string;
  change: string;
  isPositive: boolean;
  icon: any;
}

interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'DEBUG';
  module: string;
  message: string;
}

export function TelemetryPage() {
  const [ticker, setTicker] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setTicker(t => t + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  const metrics: TelemetryMetric[] = [
    {
      label: 'API Response Latency',
      value: '14.2 ms',
      change: '-1.4ms last hour',
      isPositive: true,
      icon: Activity
    },
    {
      label: 'Queue Dispatch Lag',
      value: '2.1 ms',
      change: 'Stable',
      isPositive: true,
      icon: Layers
    },
    {
      label: 'Memory Allocation',
      value: '14.8 MB',
      change: '+0.2MB peak load',
      isPositive: false,
      icon: Cpu
    },
    {
      label: 'EventBus Throughput',
      value: `${(24.2 + Math.sin(ticker / 5) * 0.5).toFixed(1)}k /s`,
      change: 'Dynamic flow',
      isPositive: true,
      icon: TrendingUp
    }
  ];

  const logFeed: LogEntry[] = [
    { timestamp: '22:14:02', level: 'INFO', module: 'api.lifespan', message: 'ExecutionScheduler backend worker starting up successfully' },
    { timestamp: '22:14:03', level: 'DEBUG', module: 'core.scheduler', message: 'FIFO queue initialization complete: semaphore(max_concurrent=3)' },
    { timestamp: '22:14:05', level: 'INFO', module: 'core.event_bus', message: 'Telemetry listener registered: ExecutionEventListener' },
    { timestamp: '22:14:10', level: 'DEBUG', module: 'core.orchestrator', message: 'Registered active Swarm roster: 5 specialist agent nodes' },
    { timestamp: '22:14:12', level: 'INFO', module: 'api.websocket', message: 'Websocket client session connected: c7df10b2' },
    { timestamp: '22:14:15', level: 'WARN', module: 'core.retry_policy', message: 'Scheduler queue dispatch delay peak exceeding threshold limit' },
    { timestamp: '22:14:18', level: 'DEBUG', module: 'core.blackboard', message: 'Memory sync successful: persisted execution state variables' },
    { timestamp: '22:14:20', level: 'INFO', module: 'api.router', message: 'GET /api/mission-control/health returned 200 OK' }
  ];

  // Generate simple CSS bar graph values dynamically
  const cpuLoadHistory = [24, 32, 45, 18, 54, 76, 32, 28, 41, 62, 34, 48, 55, 38, 22];

  return (
    <WorkspaceLayout
      title="Telemetry"
      description="Real-time system diagnostics, CPU performance analytics, and memory usage profiling."
      state="ready"
      sprintStatus="Sprint 6.0"
    >
      <ScrollableArea className="h-full w-full bg-background-dark p-6">
        <div className="max-w-6xl mx-auto space-y-6">

          {/* Metrics grids */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.map((m, idx) => {
              const Icon = m.icon;
              return (
                <Surface key={idx} variant="panel" border="strong" className="p-4 bg-surface-elevated/40 flex items-center justify-between group hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300">
                  <div className="space-y-1">
                    <span className="text-3xs font-mono text-muted uppercase tracking-wider block">{m.label}</span>
                    <span className="text-lg font-mono font-bold text-foreground group-hover:text-accent transition-colors">{m.value}</span>
                    <span className="text-3xs font-mono text-muted block">{m.change}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-surface border border-border-subtle group-hover:border-accent/20 text-muted group-hover:text-accent transition-colors">
                    <Icon className="size-4.5" />
                  </div>
                </Surface>
              );
            })}
          </div>

          {/* Performance chart grids */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* CPU Performance History - 8 Cols */}
            <div className="lg:col-span-8 flex flex-col min-h-0">
              <span className="text-xs font-mono text-muted uppercase tracking-wider mb-2">CPU Utilization Profile</span>
              <Surface variant="panel" border="strong" className="p-5 bg-surface-elevated/35 flex flex-col justify-between h-[240px]">
                <div className="flex items-end gap-2 h-36 border-b border-border-subtle pb-2">
                  {cpuLoadHistory.map((val, idx) => (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-1 group cursor-default h-full justify-end">
                      <span className="text-3xs font-mono text-muted opacity-0 group-hover:opacity-100 transition-opacity leading-none mb-1">
                        {val}%
                      </span>
                      <div 
                        className={`w-full rounded-t transition-all duration-500 bg-accent/20 border-t border-accent group-hover:bg-accent/40`} 
                        style={{ height: `${val}%` }} 
                      />
                    </div>
                  ))}
                </div>
                <div className="flex justify-between text-3xs font-mono text-muted pt-2 uppercase">
                  <span>-15 minutes ago</span>
                  <span>-7.5 minutes ago</span>
                  <span>Now</span>
                </div>
              </Surface>
            </div>

            {/* Dependency health - 4 Cols */}
            <div className="lg:col-span-4 flex flex-col min-h-0">
              <span className="text-xs font-mono text-muted uppercase tracking-wider mb-2">Telemetry Infrastructure nodes</span>
              <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/35 flex flex-col justify-between h-[240px] font-mono">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2.5 bg-surface/50 border border-border-subtle rounded-lg">
                    <div className="flex items-center gap-2">
                      <Server className="size-3.5 text-muted" />
                      <span className="text-2xs font-semibold">FastAPI Lifespan</span>
                    </div>
                    <span className="text-3xs text-emerald-400 font-bold uppercase">HEALTHY</span>
                  </div>

                  <div className="flex items-center justify-between p-2.5 bg-surface/50 border border-border-subtle rounded-lg">
                    <div className="flex items-center gap-2">
                      <Database className="size-3.5 text-muted" />
                      <span className="text-2xs font-semibold">Redis Cache node</span>
                    </div>
                    <span className="text-3xs text-emerald-400 font-bold uppercase">CONNECTED</span>
                  </div>

                  <div className="flex items-center justify-between p-2.5 bg-surface/50 border border-border-subtle rounded-lg">
                    <div className="flex items-center gap-2">
                      <Activity className="size-3.5 text-muted" />
                      <span className="text-2xs font-semibold">EventBus Listeners</span>
                    </div>
                    <span className="text-3xs font-bold text-accent">3 REGIST</span>
                  </div>
                </div>
                <div className="pt-2 border-t border-border-subtle text-3xs text-muted uppercase flex justify-between">
                  <span>Diag check</span>
                  <span>PASSED (100%)</span>
                </div>
              </Surface>
            </div>

          </div>

          {/* Scrolling log console (Bottom Row) */}
          <div className="flex flex-col min-h-[220px]">
            <span className="text-xs font-mono text-muted uppercase tracking-wider mb-2">System Telemetry Log Console</span>
            <Surface variant="panel" border="strong" className="h-[200px] bg-surface-elevated p-0 flex flex-col overflow-hidden">
              <ScrollableArea className="flex-1 p-3 bg-surface-elevated/10">
                <div className="space-y-1.5 font-mono text-2xs leading-relaxed">
                  {logFeed.map((log, idx) => {
                    const levelColors = log.level === 'WARN' ? 'text-amber-400' : log.level === 'DEBUG' ? 'text-accent' : 'text-muted';
                    return (
                      <div key={idx} className="flex gap-4 hover:bg-surface-elevated/40 p-1 rounded transition-colors">
                        <span className="text-muted/50 select-none shrink-0">{log.timestamp}</span>
                        <span className={`font-bold shrink-0 ${levelColors}`}>[{log.level}]</span>
                        <span className="text-foreground/90 shrink-0">[{log.module}]</span>
                        <span className="text-foreground/80 truncate">{log.message}</span>
                      </div>
                    );
                  })}
                </div>
              </ScrollableArea>
            </Surface>
          </div>

        </div>
      </ScrollableArea>
    </WorkspaceLayout>
  );
}
export default TelemetryPage;
