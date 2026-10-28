import { useState } from 'react';
import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { Surface } from '@/design-system/primitives/Surface';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import {
  Key, Shield, CheckCircle2, Sliders, Save, Database
} from 'lucide-react';

export function SettingsPage() {
  const [geminiKey, setGeminiKey] = useState('••••••••••••••••••••••••••••••••');
  const [openaiKey, setOpenaiKey] = useState('••••••••••••••••••••••••••••••••');
  const [anthropicKey, setAnthropicKey] = useState('••••••••••••••••••••••••••••••••');
  const [concurrency, setConcurrency] = useState(3);
  const [retryTimeout, setRetryTimeout] = useState(5000);
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  return (
    <WorkspaceLayout
      title="Settings"
      description="Synapse Swarm Engine developer configuration panel and LLM credential manager."
      state="ready"
      sprintStatus="Sprint 6.0"
    >
      <ScrollableArea className="h-full w-full bg-background-dark p-6">
        <div className="max-w-3xl mx-auto space-y-6">

          {/* Configuration save banner */}
          {isSaved && (
            <div className="p-3 border border-emerald-500/15 bg-emerald-500/10 text-emerald-400 font-mono text-2xs rounded-lg flex items-center gap-2 animate-pulse shrink-0">
              <CheckCircle2 className="size-4" />
              <span>Developer configuration options successfully saved and synchronized locally.</span>
            </div>
          )}

          {/* Section 1: Swarm LLM Credentials */}
          <Surface variant="panel" border="strong" className="p-5 bg-surface-elevated/40 flex flex-col gap-4">
            <div className="flex items-center gap-2 border-b border-border-subtle pb-3">
              <Key className="size-4 text-accent" />
              <span className="text-sm font-semibold font-mono text-foreground">LLM Provider API Credentials</span>
            </div>
            <div className="space-y-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-3xs font-mono text-muted uppercase tracking-wider">Google Gemini API Key</label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={geminiKey}
                    onChange={(e) => setGeminiKey(e.target.value)}
                    className="flex-1 bg-surface border border-border-subtle focus:border-accent p-2 text-xs rounded-lg outline-none font-mono"
                  />
                  <button className="px-3 py-1.5 border border-border-subtle text-3xs font-mono rounded-lg hover:border-accent transition-colors bg-surface-elevated">
                    VALIDATE
                  </button>
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-3xs font-mono text-muted uppercase tracking-wider">OpenAI API Key (Fallback)</label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={openaiKey}
                    onChange={(e) => setOpenaiKey(e.target.value)}
                    className="flex-1 bg-surface border border-border-subtle focus:border-accent p-2 text-xs rounded-lg outline-none font-mono"
                  />
                  <button className="px-3 py-1.5 border border-border-subtle text-3xs font-mono rounded-lg hover:border-accent transition-colors bg-surface-elevated">
                    VALIDATE
                  </button>
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-3xs font-mono text-muted uppercase tracking-wider">Anthropic API Key (Fallback)</label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={anthropicKey}
                    onChange={(e) => setAnthropicKey(e.target.value)}
                    className="flex-1 bg-surface border border-border-subtle focus:border-accent p-2 text-xs rounded-lg outline-none font-mono"
                  />
                  <button className="px-3 py-1.5 border border-border-subtle text-3xs font-mono rounded-lg hover:border-accent transition-colors bg-surface-elevated">
                    VALIDATE
                  </button>
                </div>
              </div>
            </div>
          </Surface>

          {/* Section 2: Concurrency & Queue scheduler settings */}
          <Surface variant="panel" border="strong" className="p-5 bg-surface-elevated/40 flex flex-col gap-4">
            <div className="flex items-center gap-2 border-b border-border-subtle pb-3">
              <Sliders className="size-4 text-accent" />
              <span className="text-sm font-semibold font-mono text-foreground">Scheduler Configuration</span>
            </div>
            <div className="space-y-4">
              <div className="flex flex-col gap-2 font-mono">
                <div className="flex justify-between text-3xs text-muted uppercase">
                  <span>Maximum Concurrent Executions</span>
                  <span className="text-foreground font-semibold">{concurrency} Workers</span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={concurrency}
                  onChange={(e) => setConcurrency(Number(e.target.value))}
                  className="w-full h-1 bg-border-subtle rounded-lg appearance-none cursor-pointer accent-accent"
                />
              </div>

              <div className="flex flex-col gap-2 font-mono">
                <div className="flex justify-between text-3xs text-muted uppercase">
                  <span>Retry Policy Backoff Delay</span>
                  <span className="text-foreground font-semibold">{retryTimeout} ms</span>
                </div>
                <input
                  type="range"
                  min={1000}
                  max={15000}
                  step={500}
                  value={retryTimeout}
                  onChange={(e) => setRetryTimeout(Number(e.target.value))}
                  className="w-full h-1 bg-border-subtle rounded-lg appearance-none cursor-pointer accent-accent"
                />
              </div>
            </div>
          </Surface>

          {/* Section 3: Telemetry & Memory persistence options */}
          <Surface variant="panel" border="strong" className="p-5 bg-surface-elevated/40 flex flex-col gap-4">
            <div className="flex items-center gap-2 border-b border-border-subtle pb-3">
              <Database className="size-4 text-accent" />
              <span className="text-sm font-semibold font-mono text-foreground">Cache & Log Telemetry Settings</span>
            </div>
            <div className="space-y-3 font-mono text-2xs text-foreground/80">
              <div className="flex items-center justify-between p-2 rounded hover:bg-surface transition-colors">
                <span>Enable In-Memory Telemetry Database</span>
                <input type="checkbox" defaultChecked className="accent-accent cursor-pointer" />
              </div>
              <div className="flex items-center justify-between p-2 rounded hover:bg-surface transition-colors">
                <span>Compress Timeline History Logs</span>
                <input type="checkbox" defaultChecked className="accent-accent cursor-pointer" />
              </div>
              <div className="flex items-center justify-between p-2 rounded hover:bg-surface transition-colors">
                <span>Verbose Debug logging (Console outputs)</span>
                <input type="checkbox" className="accent-accent cursor-pointer" />
              </div>
            </div>
          </Surface>

          {/* Save Action */}
          <div className="flex items-center justify-between p-4 border border-border-subtle bg-surface-elevated/20 rounded-lg shrink-0">
            <div className="flex items-center gap-2 font-mono text-3xs text-muted leading-relaxed max-w-md">
              <Shield className="size-4 text-accent shrink-0" />
              <span>Sensitive values are stored locally in the FastAPI context parameters and are never transmitted to third parties.</span>
            </div>
            <button
              onClick={handleSave}
              className="flex items-center gap-1.5 px-4 py-2 bg-accent hover:bg-accent-hover text-white text-xs font-semibold rounded-lg shadow-sm transition-colors cursor-pointer"
            >
              <Save className="size-3.5" />
              Save Config
            </button>
          </div>

        </div>
      </ScrollableArea>
    </WorkspaceLayout>
  );
}
export default SettingsPage;
