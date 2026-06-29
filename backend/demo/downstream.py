"""Simulates downstream enterprise systems reacting to arbitration cycles."""

from typing import Dict, List

from schemas.consensus import ConsensusOutput


class DownstreamSystemSimulator:
    """Simulates automated enterprise systems reacting to evidence cycles."""

    def __init__(self) -> None:
        """Initializes the downstream systems with nominal state."""
        self.systems = [
            "Fuel Procurement",
            "Route Optimizer",
            "Insurance Pricing",
            "Scheduling Engine",
        ]

    def process_cycle(
        self, cycle_id: int, consensus: ConsensusOutput
    ) -> List[Dict[str, str]]:
        """Determines the state of downstream systems based on the consensus."""

        is_panic = cycle_id < 4 and consensus.confidence < 0.8
        is_recovering = cycle_id == 4

        state_key = (
            "panic" if is_panic else "recovering" if is_recovering else "nominal"
        )

        states = {
            "Fuel Procurement": {
                "panic": "PANIC BUYING - Spot Market (+400% Markup)",
                "recovering": "HALTING SPOT BUYS - Re-evaluating",
                "nominal": "NOMINAL - Long term contracts active",
            },
            "Route Optimizer": {
                "panic": "REROUTING - Avoiding Suez Canal (+14 days)",
                "recovering": "CANCELING REROUTE - Holding position",
                "nominal": "NOMINAL - Standard routing active",
            },
            "Insurance Pricing": {
                "panic": "PREMIUM SURGE - High Risk Zone Triggered",
                "recovering": "PREMIUM RECALCULATING",
                "nominal": "NOMINAL - Standard risk profile",
            },
            "Scheduling Engine": {
                "panic": "CASCADE DELAY - Port slots missed",
                "recovering": "RESCHEDULING - Attempting slot recovery",
                "nominal": "NOMINAL - On schedule",
            },
        }

        results = []
        for system in self.systems:
            status = states.get(system, {}).get(state_key, "UNKNOWN")
            results.append({"system": system, "status": status})

        return results
