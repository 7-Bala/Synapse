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
        results = []

        # We simulate the panic of enterprise systems during early uncertainty/contradiction
        # and the stabilization once consensus is reached.
        is_panic = cycle_id < 4 and consensus.confidence < 0.8
        is_recovering = cycle_id == 4

        for system in self.systems:
            if system == "Fuel Procurement":
                if is_panic:
                    status = "PANIC BUYING - Spot Market (+400% Markup)"
                elif is_recovering:
                    status = "HALTING SPOT BUYS - Re-evaluating"
                else:
                    status = "NOMINAL - Long term contracts active"

            elif system == "Route Optimizer":
                if is_panic:
                    status = "REROUTING - Avoiding Suez Canal (+14 days)"
                elif is_recovering:
                    status = "CANCELING REROUTE - Holding position"
                else:
                    status = "NOMINAL - Standard routing active"

            elif system == "Insurance Pricing":
                if is_panic:
                    status = "PREMIUM SURGE - High Risk Zone Triggered"
                elif is_recovering:
                    status = "PREMIUM RECALCULATING"
                else:
                    status = "NOMINAL - Standard risk profile"

            elif system == "Scheduling Engine":
                if is_panic:
                    status = "CASCADE DELAY - Port slots missed"
                elif is_recovering:
                    status = "RESCHEDULING - Attempting slot recovery"
                else:
                    status = "NOMINAL - On schedule"

            results.append({"system": system, "status": status})

        return results
