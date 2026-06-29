import { WorkspaceGrid } from '@/design-system/layout/WorkspaceGrid';
import { Stack } from '@/design-system/primitives/Stack';
import { Terminal } from 'lucide-react';
import { useExecutionStore } from '@/stores/executionStore';
import { ExecutionNodeComponent } from './ExecutionNodeComponent';


export function ExecutionGraph() {
  const { executionGraph, selectedNode, selectNode } = useExecutionStore();

  const triggerDemo = async () => {
    try {
      await fetch('http://localhost:8000/demo/start', { method: 'POST' });
    } catch (e) {
      console.error('Failed to trigger demo', e);
    }
  };

  return (
    <div className="relative flex-1 w-full h-full bg-background">
      <WorkspaceGrid gridSize={30}>
        {/* Global Topology Heatmap Overlay */}
        <div className="absolute inset-0 p-6 pointer-events-none z-10 flex justify-between items-start">
          <Stack gap={1}>
            <h2 className="text-lg font-sans font-semibold tracking-tight text-foreground drop-shadow-md">Execution Topology</h2>
            {!executionGraph && (
              <span className="text-xs font-mono text-muted uppercase tracking-wider">No Active Execution</span>
            )}
          </Stack>
        </div>

        {/* Simulated Nodes & Dynamic Graph */}
        {!executionGraph && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Stack gap={4} className="items-center">
              <Terminal className="size-12 text-muted" />
              <div className="text-muted text-sm uppercase tracking-widest font-mono">Connect to an Orchestrator or Start a New Execution</div>
              <button onClick={triggerDemo} className="px-4 py-2 border border-accent text-accent rounded hover:bg-accent/10 transition-colors text-xs font-mono uppercase tracking-widest">Start Demo Execution</button>
            </Stack>
          </div>
        )}

        {executionGraph && executionGraph.nodes.map((node, index) => {
          // Basic linear layout for demo purposes
          const x = 100 + (index * 200);
          const y = 150;
          return (
            <ExecutionNodeComponent 
              key={node.id}
              id={node.id}
              label={node.agentName || node.id}
              status={node.status}
              x={x}
              y={y}
              selected={selectedNode === node.id}
              onClick={() => selectNode(node.id)}
            />
          );
        })}
        
        {/* Connecting Lines for sequential nodes */}
        {executionGraph && executionGraph.nodes.map((_, index) => {
          if (index === executionGraph.nodes.length - 1) return null;
          const x1 = 100 + (index * 200) + 100;
          const y1 = 150 + 20;
          const x2 = 100 + ((index + 1) * 200);
          
          const isRunning = executionGraph.nodes[index + 1].status === 'RUNNING';
          
          return (
            <svg key={`edge-${index}`} className="absolute inset-0 w-full h-full pointer-events-none">
              <path 
                d={`M ${x1} ${y1} L ${x2} ${y1}`} 
                fill="none" 
                stroke={isRunning ? "#3B82F6" : "#3F3F46"} 
                strokeWidth={isRunning ? "1.5" : "1"} 
                strokeDasharray={isRunning ? "4 8" : "none"} 
                className={isRunning ? "animate-[dash_2s_linear_infinite]" : ""}
              />
            </svg>
          );
        })}
      </WorkspaceGrid>
    </div>
  );
}
