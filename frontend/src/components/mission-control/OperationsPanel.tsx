import { Stack } from '@/design-system/primitives/Stack';
import { Section } from '@/design-system/primitives/Section';
import { PlayCircle } from 'lucide-react';

export function OperationsPanel() {
  const triggerDemo = async () => {
    try {
      await fetch('http://localhost:8000/demo/start', { method: 'POST' });
    } catch (e) {
      console.error('Failed to trigger demo', e);
    }
  };

  return (
    <Section title="Operations">
      <Stack gap={2}>
        <button 
          onClick={triggerDemo}
          className="flex items-center gap-2 w-full p-2 text-xs text-foreground hover:bg-accent/10 border border-border-subtle hover:border-accent/50 rounded transition-colors text-left font-medium"
        >
          <PlayCircle className="size-3.5 text-accent" />
          Start Demo Execution
        </button>
      </Stack>
    </Section>
  );
}
