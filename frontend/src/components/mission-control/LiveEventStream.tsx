import { RuntimeEventExplorer } from '@/components/runtime-events/RuntimeEventExplorer';

/**
 * @deprecated Use RuntimeEventExplorer directly.
 * This component is kept as a lightweight wrapper to preserve git history and backwards compatibility.
 */
export function LiveEventStream() {
  return <RuntimeEventExplorer compact />;
}
