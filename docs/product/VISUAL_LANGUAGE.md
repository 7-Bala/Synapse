# Visual Language Principles

## What should Synapse feel like?
Synapse should feel like a high-performance command terminal wrapped in modern glassmorphism. It is not a playful consumer app. It is a serious, deterministic, and precise engineering tool. It should feel like a Bloomberg Terminal for AI.

## How should professionals feel after using it for eight hours?
Unfatigued. 
- Contrast must be accessible but not glaring.
- Dark mode (`enterprise-dark`) is the default and optimized for long-session eye strain reduction.
- Information must be dense but perfectly aligned.

## What should motion communicate?
- **Never decorative.**
- Motion explains state transitions (e.g., an agent passing a token to another agent).
- Motion directs attention (e.g., a subtle pulse on a node requiring human approval).
- Must respect `prefers-reduced-motion`.

## What should color communicate?
- **Strictly semantic.**
- Grey/Monochrome: Static infrastructure, un-executed nodes.
- Blue/Brand: Active processes, processing states.
- Green/Amber/Red: Strictly reserved for Success, Warning/Blocked, Error/Halted.
- Never use color for aesthetic variety.

## What makes a Synapse screenshot instantly recognizable?
The rigid, highly structured `WorkspaceGrid` background, the ubiquitous right-aligned `InspectorLayout`, and the dense, monospaced data visualization overlays.
