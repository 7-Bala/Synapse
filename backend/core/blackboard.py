"""Blackboard implementation for the Synapse backend."""

import copy
from typing import Dict, List, Optional

from schemas.blackboard import BlackboardEntry


class Blackboard:
    """An append-only blackboard for storing agent outputs."""

    def __init__(self) -> None:
        """Initializes an empty blackboard."""
        self._entries: List[BlackboardEntry] = []

    def append(self, entry: BlackboardEntry) -> None:
        """Appends a new entry to the blackboard."""
        self._entries.append(entry)

    def get_all(self) -> List[BlackboardEntry]:
        """Returns all entries in the blackboard."""
        return self._entries.copy()

    def get_current_state(self) -> Dict[str, BlackboardEntry]:
        """Returns the latest entry for each agent.

        Returns:
            Dict[str, BlackboardEntry]: A mapping of agent names to their latest entry.
        """
        state = {}
        # Iterate in order so later entries overwrite earlier ones for the same agent
        for entry in self._entries:
            state[entry.agent_name] = entry
        return state

    def snapshot(self) -> List[BlackboardEntry]:
        """Returns a deep copy of all entries for immutable context passing."""
        return copy.deepcopy(self._entries)

    def latest_tick(self) -> int:
        """Returns the ID of the most recent tick that has entries.

        Returns:
            int: The latest tick ID, or -1 if the blackboard is empty.
        """
        if not self._entries:
            return -1
        return max(entry.tick_id for entry in self._entries)

    def entries_for_tick(self, tick_id: int) -> List[BlackboardEntry]:
        """Returns all entries generated during a specific tick."""
        return [entry for entry in self._entries if entry.tick_id == tick_id]

    def latest_entry(self, agent_name: str) -> Optional[BlackboardEntry]:
        """Returns the latest entry produced by a specific agent."""
        for entry in reversed(self._entries):
            if entry.agent_name == agent_name:
                return entry
        return None
