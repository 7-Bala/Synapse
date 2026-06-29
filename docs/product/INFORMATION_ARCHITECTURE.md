# Information Architecture

## Guiding Principles
- **Progressive Disclosure:** Never overload the screen. Show high-level state first. Reveal raw JSON only when explicitly requested (e.g., via the Inspector).
- **Context is King:** Never navigate the user away from their current debugging context. Use slide-out panels (Inspectors) instead of new pages.

## Example: Execute Workspace

### Primary Information (Always visible, highest contrast)
- Swarm Status (Running, Blocked, Failed)
- Topology Graph (The visual relationship of agents)
- Critical alerts (e.g., "Human approval required for tool call")

### Secondary Information (Visible but subdued)
- Active Node names
- Execution duration
- Token spend so far

### Supporting Information (Available via single click / Hover)
- Agent Prompts
- Tool definitions (Schemas)
- Intermediate reasoning tokens (CoT)

### Hidden Information (Requires intentional drill-down)
- Raw HTTP request/response payloads to the LLM API
- Full memory history (Blackboard complete dump)
- Infrastructure node IDs
